import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()




# 환경 변수 로드
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
# AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
# DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_MODEL")
# DEPLOYMENT_EMBEDDING_NAME = os.getenv("AZURE_DEPLOYMENT_EMBEDDING_NAME")
INDEX_NAME = "tibero-vector"

# Azure OpenAI 클라이언트 초기화
chat_client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2024-12-01-preview",
)

# 메시지 히스토리 초기화
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant that helps people find information.",
    }
]


def get_answer(question):
    """질문에 대한 답변을 생성합니다."""
    # 사용자 메시지 추가
    messages.append({"role": "user", "content": question})

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
        print("Generating answer...")
        response = chat_client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            extra_body=rag_params,
        )

        answer = response.choices[0].message.content

        # 어시스턴트 메시지 저장
        messages.append({"role": "assistant", "content": answer})

        return answer

    except Exception as e:
        return f"Error occurred: {str(e)}"


def main():
    """메인 실행 함수"""
    print("=== Azure AI Search RAG Chatbot ===")
    print("Type 'quit' or 'exit' to stop the program.\n")

    while True:
        # 사용자 입력 받기
        question = input("Enter your question: ").strip()

        # 종료 조건
        if question.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # 빈 입력 체크
        if not question:
            print("Please enter a question.\n")
            continue

        # 답변 생성 및 출력
        answer = get_answer(question)
        print(f"\nResponse:\n{answer}\n")
        print("-" * 50 + "\n")


if __name__ == "__main__":
    main()
