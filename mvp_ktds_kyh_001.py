#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure OpenAI RAG Chatbot - Streamlit 웹 인터페이스
Tibero 문서 검색 및 질의응답 시스템
"""

import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from openai import AzureOpenAI

# 환경 변수 로드
load_dotenv()

# Azure 설정
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT_MODEL = os.getenv("AZURE_DEPLOYMENT_MODEL")
AZURE_DEPLOYMENT_EMBEDDING_NAME = os.getenv("AZURE_DEPLOYMENT_EMBEDDING_NAME")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")


# 페이지 설정
st.set_page_config(
    page_title="안녕하세요. 챗봇입니다.",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_chat_client():
    """Azure OpenAI 클라이언트 생성 (캐시)"""
    # 프록시 환경 변수 제거 (문제 해결)
    env_vars_to_remove = ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]
    for var in env_vars_to_remove:
        if var in os.environ:
            del os.environ[var]

    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=API_VERSION,
        timeout=60.0,  # 타임아웃 명시적 설정
    )


def create_system_message():
    """시스템 메시지 생성"""
    return {
        "role": "system",
        "content": (
            "당신은 Tibero 데이터베이스 전문가입니다. "
            "사용자의 질문에 대해 검색된 문서를 바탕으로 정확하고 상세하게 답변하세요. "
            "답변 시 다음을 준수하세요:\n"
            "1. 검색된 문서의 내용을 기반으로 답변\n"
            "2. 답변이 불확실한 경우 '확실하지 않습니다'라고 명시\n"
            "3. 가능한 한 구체적인 예시와 함께 설명\n"
            "4. 출처가 있는 경우 출처를 언급"
        ),
    }


def create_rag_parameters(top_n=5, strictness=3):
    """RAG 파라미터 생성"""
    return {
        "data_sources": [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": AZURE_SEARCH_ENDPOINT,
                    "index_name": INDEX_NAME,
                    "authentication": {
                        "type": "api_key",
                        "key": AZURE_SEARCH_API_KEY,
                    },
                    "query_type": "vector",
                    "embedding_dependency": {
                        "type": "deployment_name",
                        "deployment_name": AZURE_DEPLOYMENT_EMBEDDING_NAME,
                    },
                    "top_n_documents": top_n,
                    "strictness": strictness,
                },
            }
        ],
    }


def get_answer(
    chat_client,
    messages,
    question,
    temperature=0.7,
    max_tokens=1000,
    top_n=5,
    strictness=3,
):
    """질문에 대한 답변 생성"""
    # 사용자 메시지 추가
    user_message = {"role": "user", "content": question}
    messages.append(user_message)

    # RAG 파라미터
    rag_params = create_rag_parameters(top_n, strictness)

    try:
        response = chat_client.chat.completions.create(
            model=AZURE_DEPLOYMENT_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_body=rag_params,
        )

        # 답변 추출
        answer = response.choices[0].message.content

        # 어시스턴트 메시지 저장
        assistant_message = {"role": "assistant", "content": answer}
        messages.append(assistant_message)

        # 인용 정보 추출
        citations = []
        if hasattr(response.choices[0].message, "context"):
            context = response.choices[0].message.context
            if context and "citations" in context:
                citations = context["citations"]

        return answer, citations, None

    except Exception as e:
        return None, [], str(e)


def initialize_session_state():
    """세션 상태 초기화"""
    if "messages" not in st.session_state:
        st.session_state.messages = [create_system_message()]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "chat_client" not in st.session_state:
        st.session_state.chat_client = get_chat_client()

    # 메시지 ID 카운터 추가
    if "message_counter" not in st.session_state:
        st.session_state.message_counter = 0


def reset_conversation():
    """대화 초기화"""
    st.session_state.messages = [create_system_message()]
    st.session_state.chat_history = []
    st.session_state.message_counter = 0
    st.success("✓ 대화가 초기화되었습니다.")


def remove_duplicate_citations(citations):
    """중복 인용 제거 (제목 기준)"""
    if not citations:
        return []

    seen_titles = set()
    unique_citations = []

    for citation in citations:
        title = citation.get("title", "제목 없음")
        # 제목이 이미 본 것이 아니면 추가
        if title not in seen_titles:
            seen_titles.add(title)
            unique_citations.append(citation)

    return unique_citations


def display_chat_message(
    role, content, timestamp=None, citations=None, message_id=None
):
    """채팅 메시지 표시"""
    avatar = "🧑" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):
        st.markdown(content)

        # 타임스탬프 표시
        if timestamp:
            st.caption(f"🕐 {timestamp}")

        # 인용 정보 표시 (assistant 메시지에만, 중복 제거, 항상 닫힌 상태)
        # 중요: user 메시지에는 citations를 표시하지 않음!
        if role == "assistant" and citations:
            unique_citations = remove_duplicate_citations(citations)
            with st.expander(
                f"📚 참고 문서 ({len(unique_citations)}개)",
                expanded=False,  # 항상 닫힌 상태로 표시
            ):
                for i, citation in enumerate(unique_citations, 1):
                    title = citation.get("title", "제목 없음")
                    url = citation.get("url", "")
                    st.markdown(f"**{i}. {title}**")
                    if url:
                        st.markdown(f"   🔗 [{url}]({url})")


def main():
    """메인 함수"""
    # 세션 상태 초기화
    initialize_session_state()

    # 헤더
    st.title("🤖 안녕하세요. 챗봇입니다.")
    st.markdown("Tibero 데이터베이스 문서 검색 및 질의응답 시스템")
    st.divider()

    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")

        # 모델 설정
        st.subheader("🎛️ 모델 파라미터")
        temperature = st.slider(
            "Temperature (창의성)",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="높을수록 창의적이지만 일관성이 낮아집니다",
        )

        max_tokens = st.slider(
            "Max Tokens (최대 길이)",
            min_value=100,
            max_value=2000,
            value=1000,
            step=100,
            help="생성할 답변의 최대 토큰 수",
        )

        st.divider()

        # RAG 설정
        st.subheader("🔍 검색 설정")
        top_n = st.slider(
            "검색 문서 수",
            min_value=1,
            max_value=10,
            value=5,
            help="검색할 문서의 개수",
        )

        strictness = st.slider(
            "관련성 엄격도",
            min_value=1,
            max_value=5,
            value=3,
            help="높을수록 관련성이 높은 문서만 사용",
        )

        st.divider()

        # 시스템 정보
        st.subheader("ℹ️ 시스템 정보")
        with st.expander("상세 정보 보기"):
            st.text(f"GPT Model: {AZURE_DEPLOYMENT_MODEL}")
            st.text(f"Embedding: {AZURE_DEPLOYMENT_EMBEDDING_NAME}")
            st.text(f"Search Index: {INDEX_NAME}")
            st.text(f"API Version: {API_VERSION}")

        st.divider()

        # 대화 관리
        st.subheader("💬 대화 관리")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 초기화", use_container_width=True):
                reset_conversation()
                st.rerun()

        with col2:
            if st.button("📊 통계", use_container_width=True):
                msg_count = len(
                    [m for m in st.session_state.messages if m["role"] != "system"]
                )
                st.info(f"총 {msg_count}개 메시지")

        # 대화 내보내기
        if st.session_state.chat_history:
            st.divider()
            if st.button("💾 대화 저장", use_container_width=True):
                import json

                conversation = {
                    "timestamp": datetime.now().isoformat(),
                    "messages": st.session_state.chat_history,
                }
                st.download_button(
                    label="📥 JSON 다운로드",
                    data=json.dumps(conversation, ensure_ascii=False, indent=2),
                    file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                )

    # 메인 채팅 영역
    st.subheader("💭 채팅")

    # 채팅 히스토리 표시
    for i, chat in enumerate(st.session_state.chat_history):
        # 중요: user 메시지는 citations를 None으로 강제!
        chat_citations = chat.get("citations") if chat["role"] == "assistant" else None

        display_chat_message(
            role=chat["role"],
            content=chat["content"],
            timestamp=chat.get("timestamp"),
            citations=chat_citations,  # user는 항상 None, assistant만 citations
            message_id=chat.get("message_id", i),
        )

    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요..."):
        # 메시지 ID 증가
        st.session_state.message_counter += 1
        user_message_id = st.session_state.message_counter

        # 사용자 메시지 표시 (citations=None, 참고 문서 없음!)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        display_chat_message(
            "user", prompt, timestamp, citations=None, message_id=user_message_id
        )

        # 채팅 히스토리에 추가 (citations 없이!)
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": prompt,
                "timestamp": timestamp,
                "message_id": user_message_id,
                # citations 필드 없음!
            }
        )

        # 답변 생성
        with st.spinner("🤔 답변 생성 중..."):
            answer, citations, error = get_answer(
                st.session_state.chat_client,
                st.session_state.messages,
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_n=top_n,
                strictness=strictness,
            )

        # 답변 표시
        if error:
            st.error(f"❌ 오류 발생: {error}")
        else:
            # 메시지 ID 증가
            st.session_state.message_counter += 1
            assistant_message_id = st.session_state.message_counter

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # assistant 메시지만 citations 포함
            display_chat_message(
                "assistant", answer, timestamp, citations, assistant_message_id
            )

            # 채팅 히스토리에 추가 (citations 포함!)
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "timestamp": timestamp,
                    "citations": citations,  # assistant만 citations 있음!
                    "message_id": assistant_message_id,
                }
            )

    # 빈 공간 (스크롤을 위해)
    st.write("")
    st.write("")

    # 푸터
    st.divider()
    # st.caption("🔒 Powered by Azure OpenAI & Azure Cognitive Search")


if __name__ == "__main__":
    main()
