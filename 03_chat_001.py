#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure OpenAI RAG Chatbot - 개선 버전
Tibero 문서 검색 및 질의응답 시스템
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# 환경 변수 로드
load_dotenv()

# Azure 설정 - 환경 변수 우선, 없으면 하드코딩된 값 사용
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT_MODEL = os.getenv("AZURE_DEPLOYMENT_MODEL")
AZURE_DEPLOYMENT_EMBEDDING_NAME = os.getenv("AZURE_DEPLOYMENT_EMBEDDING_NAME")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")


def create_chat_client():
    """Azure OpenAI 클라이언트 생성"""
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=API_VERSION,
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
        )
    }


def create_rag_parameters():
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
                    "top_n_documents": 5,  # 검색할 문서 수
                    "strictness": 3,  # 관련성 엄격도 (1-5, 높을수록 엄격)
                },
            }
        ],
    }


def get_answer(chat_client, messages, question):
    """질문에 대한 답변을 생성합니다.
    
    Args:
        chat_client: Azure OpenAI 클라이언트
        messages: 대화 히스토리
        question: 사용자 질문
        
    Returns:
        tuple: (답변 텍스트, 인용 정보)
    """
    # 사용자 메시지 추가
    messages.append({"role": "user", "content": question})

    # RAG 파라미터
    rag_params = create_rag_parameters()

    try:
        print("\n답변 생성 중...", end=" ", flush=True)
        
        response = chat_client.chat.completions.create(
            model=AZURE_DEPLOYMENT_MODEL,
            messages=messages,
            temperature=0.7,  # 창의성 조절 (0-1)
            max_tokens=1000,  # 최대 토큰 수
            extra_body=rag_params,
        )

        # 답변 추출
        answer = response.choices[0].message.content
        
        # 어시스턴트 메시지 저장
        messages.append({"role": "assistant", "content": answer})
        
        # 인용 정보 추출 (있는 경우)
        citations = []
        if hasattr(response.choices[0].message, 'context'):
            context = response.choices[0].message.context
            if context and 'citations' in context:
                citations = context['citations']
        
        print("완료!")
        
        return answer, citations

    except Exception as e:
        error_msg = f"오류 발생: {str(e)}"
        print(f"\n❌ {error_msg}")
        return error_msg, []



def remove_duplicate_citations(citations):
    """중복 인용 제거 (제목 기준)
    
    Args:
        citations: 인용 정보 리스트
        
    Returns:
        list: 중복이 제거된 인용 정보 리스트
    """
    if not citations:
        return []
    
    seen_titles = set()
    unique_citations = []
    
    for citation in citations:
        title = citation.get('title', '제목 없음')
        # 제목이 이미 본 것이 아니면 추가
        if title not in seen_titles:
            seen_titles.add(title)
            unique_citations.append(citation)
    
    return unique_citations


def display_answer(answer, citations=None):
    """답변과 인용 정보를 표시합니다."""
    print("\n" + "=" * 70)
    print("답변:")
    print("=" * 70)
    print(answer)
    
    # 인용 정보가 있는 경우 표시 (중복 제거)
    if citations:
        unique_citations = remove_duplicate_citations(citations)
        print("\n" + "-" * 70)
        print(f"참고 문서: ({len(unique_citations)}개)")
        print("-" * 70)
        for i, citation in enumerate(unique_citations, 1):
            title = citation.get('title', '제목 없음')
            url = citation.get('url', '')
            print(f"{i}. {title}")
            if url:
                print(f"   URL: {url}")
    
    print("=" * 70 + "\n")

def display_conversation_history(messages):
    """대화 히스토리 표시"""
    print("\n" + "=" * 70)
    print("대화 히스토리:")
    print("=" * 70)
    
    for i, msg in enumerate(messages[1:], 1):  # 시스템 메시지 제외
        role = "사용자" if msg["role"] == "user" else "어시스턴트"
        content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
        print(f"{i}. [{role}] {content}")
    
    print("=" * 70 + "\n")


def reset_conversation(messages):
    """대화 초기화"""
    messages.clear()
    messages.append(create_system_message())
    print("✓ 대화가 초기화되었습니다.\n")


def show_help():
    """도움말 표시"""
    print("\n" + "=" * 70)
    print("명령어:")
    print("=" * 70)
    print("  help         - 도움말 표시")
    print("  history      - 대화 히스토리 표시")
    print("  reset        - 대화 초기화")
    print("  settings     - 현재 설정 표시")
    print("  quit / exit  - 프로그램 종료")
    print("=" * 70 + "\n")


def show_settings():
    """현재 설정 표시"""
    print("\n" + "=" * 70)
    print("현재 설정:")
    print("=" * 70)
    print(f"OpenAI Endpoint:  {AZURE_OPENAI_ENDPOINT}")
    print(f"Search Endpoint:  {AZURE_SEARCH_ENDPOINT}")
    print(f"Index Name:       {INDEX_NAME}")
    print(f"GPT Model:        {AZURE_DEPLOYMENT_MODEL}")
    print(f"Embedding Model:  {AZURE_DEPLOYMENT_EMBEDDING_NAME}")
    print(f"API Version:      {API_VERSION}")
    print("=" * 70 + "\n")


def main():
    """메인 실행 함수"""
    print("\n" + "=" * 70)
    print("Azure OpenAI RAG Chatbot - Tibero 문서 검색")
    print("=" * 70)
    print("\n환경 설정 확인 중...")
    
    # 설정 확인
    if not all([AZURE_OPENAI_API_KEY, AZURE_SEARCH_API_KEY, 
                AZURE_OPENAI_ENDPOINT, AZURE_SEARCH_ENDPOINT]):
        print("❌ 오류: 필수 환경 변수가 설정되지 않았습니다.")
        print("AZURE_OPENAI_API_KEY, AZURE_SEARCH_API_KEY 등을 확인하세요.")
        return
    
    print("✓ 환경 설정 완료")
    
    # OpenAI 클라이언트 생성
    try:
        chat_client = create_chat_client()
        print("✓ Azure OpenAI 클라이언트 생성 완료")
    except Exception as e:
        print(f"❌ 클라이언트 생성 실패: {e}")
        return
    
    # 메시지 히스토리 초기화
    messages = [create_system_message()]
    
    print("\n사용 가능한 명령어를 보려면 'help'를 입력하세요.")
    print("질문을 시작하세요!\n")
    
    # 메인 루프
    while True:
        try:
            # 사용자 입력 받기
            question = input("질문: ").strip()
            
            # 빈 입력 체크
            if not question:
                continue
            
            # 종료 명령
            if question.lower() in ["quit", "exit", "q"]:
                print("\n프로그램을 종료합니다. 감사합니다!")
                break
            
            # 명령어 처리
            if question.lower() == "help":
                show_help()
                continue
            
            if question.lower() == "history":
                display_conversation_history(messages)
                continue
            
            if question.lower() == "reset":
                reset_conversation(messages)
                continue
            
            if question.lower() == "settings":
                show_settings()
                continue
            
            # 답변 생성 및 표시
            answer, citations = get_answer(chat_client, messages, question)
            display_answer(answer, citations)
            
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류 발생: {e}")
            print("다시 시도하거나 'quit'를 입력하여 종료하세요.\n")


if __name__ == "__main__":
    main()