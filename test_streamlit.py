import os
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# 환경 변수 로드
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_MODEL")
DEPLOYMENT_EMBEDDING_NAME = os.getenv("AZURE_DEPLOYMENT_EMBEDDING_NAME")
INDEX_NAME = "tibero-vector"

# Tibero 전문가 시스템 프롬프트
TIBERO_SYSTEM_PROMPT = """너는 Tibero 데이터베이스 전문가이자 기술문서 요약 AI야. 
입력된 Tibero 기술문서나 오류 로그를 분석해서 다음을 생성해:

1) 요약 (핵심 구조, 개념, 절차)
2) 오류/에러코드 분석 (원인, 조치, 관련 매뉴얼 섹션)
3) 추가 확인 필요사항 2가지

항상 명확하고 구조화된 형식으로 답변하며, Tibero 데이터베이스의 특성을 고려한 실용적인 조언을 제공해.

**출력 형식 예시:**

요약: 서버 응답 대기 중 타임아웃 발생. 네트워크 지연 혹은 리스너 설정 문제 가능.

오류 분석:
- 원인: (1) 서버 비가동 또는 리스너 비활성화 (2) 방화벽 포트 차단 (3) 네트워크 지연
- 조치: listener.ora 확인, ping 테스트, 방화벽 8629 포트 허용
- 참고: Tibero Admin Guide 3.4절

추가 확인 필요:
1. DB Listener 상태
2. OS 방화벽 정책

확신도: 높음"""

# Azure OpenAI 클라이언트 초기화
@st.cache_resource
def get_chat_client():
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version="2024-12-01-preview",
    )

chat_client = get_chat_client()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": TIBERO_SYSTEM_PROMPT,
        }
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def get_answer(question):
    """질문에 대한 답변을 생성합니다."""
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": question})

    # Azure AI Search RAG 파라미터
    rag_params = {
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
                        "deployment_name": DEPLOYMENT_EMBEDDING_NAME,
                    },
                },
            }
        ],
    }

    try:
        response = chat_client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=st.session_state.messages,
            extra_body=rag_params,
        )

        answer = response.choices[0].message.content

        # 어시스턴트 메시지 저장
        st.session_state.messages.append({"role": "assistant", "content": answer})

        return answer

    except Exception as e:
        # 오류 발생 시 마지막 사용자 메시지 제거
        st.session_state.messages.pop()
        return f"Error occurred: {str(e)}"


def main():
    """메인 Streamlit UI"""
    st.title("🗄️ Tibero Database Expert Assistant")
    st.markdown("*Tibero 데이터베이스 전문 기술문서 분석 및 오류 해결 도우미*")
    st.markdown("---")

    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ Settings")
        st.info(f"**Model:** {DEPLOYMENT_NAME}")
        st.info(f"**Index:** {INDEX_NAME}")
        
        st.markdown("---")
        st.subheader("📋 AI 역할")
        st.markdown("""
        - ✅ Tibero 기술문서 요약
        - ✅ 오류/에러코드 분석
        - ✅ 원인 및 조치방법 제시
        - ✅ 추가 확인사항 안내
        """)
        
        st.markdown("---")
        st.subheader("📝 출력 형식 예시")
        with st.expander("예시 보기"):
            st.markdown("""
**요약:** 서버 응답 대기 중 타임아웃 발생. 네트워크 지연 혹은 리스너 설정 문제 가능.

**오류 분석:**
- 원인: (1) 서버 비가동 또는 리스너 비활성화 (2) 방화벽 포트 차단 (3) 네트워크 지연
- 조치: listener.ora 확인, ping 테스트, 방화벽 8629 포트 허용
- 참고: Tibero Admin Guide 3.4절

**추가 확인 필요:**
1. DB Listener 상태
2. OS 방화벽 정책

**확신도:** 높음
            """)
        
        st.markdown("---")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": TIBERO_SYSTEM_PROMPT,
                }
            ]
            st.session_state.chat_history = []
            st.rerun()

    # 안내 메시지 (채팅이 비어있을 때만 표시)
    if not st.session_state.chat_history:
        st.info("💡 **사용 방법:** Tibero 기술문서나 오류 로그를 입력하면 AI가 자동으로 분석하여 요약, 오류 분석, 추가 확인사항을 제공합니다.")
        
        with st.expander("📌 예시 질문"):
            st.markdown("""
            - `TNS-12170: Connect timeout occurred` 오류가 발생했어요
            - Tibero 리스너 설정 방법을 알려주세요
            - 데이터베이스 연결이 끊기는 문제를 해결하고 싶어요
            - TB-31603 에러코드 의미가 뭔가요?
            """)

    # 채팅 히스토리 표시
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    # 사용자 입력
    if question := st.chat_input("Tibero 기술문서나 오류 로그를 입력하세요..."):
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.markdown(question)
        
        # 채팅 히스토리에 추가
        st.session_state.chat_history.append({"role": "user", "content": question})

        # 답변 생성
        with st.chat_message("assistant"):
            with st.spinner("Tibero 전문가가 분석 중입니다..."):
                answer = get_answer(question)
                st.markdown(answer)
        
        # 채팅 히스토리에 추가
        st.session_state.chat_history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()