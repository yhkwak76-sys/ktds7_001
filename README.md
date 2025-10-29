# ktds7_001
ktds MS AI 과정 7기 Repository


1. 이름
2. 프로젝트명
   - AI를 활용한 기술문서 자동 요약 및 오류 분석
3. 간단한설명
   - 자료 : Tibero 관련 기술문서, 로그, 매뉴얼 등
   - AI가 자동으로 핵심 개념 요약, 주요 오류/원인 설명, 해결 가이드 생성
4. 깃허브 링크
   - https://github.com/yhkwak76-sys/ktds7_001.git


# 🤖 Azure OpenAI RAG Chatbot (Tibero 문서 검색)

이 프로젝트는 **Azure OpenAI**와 **Azure AI Search**를 활용한  
**Tibero 데이터베이스 기술문서 기반 질의응답 시스템**입니다.  
Streamlit 웹 인터페이스를 통해 Tibero 관련 질문을 입력하면,  
벡터 검색으로 문서를 찾아 정확한 답변을 제공합니다.

---

## 📘 프로젝트 개요

| 항목 | 설명 |
|------|------|
| **프로젝트명** | Azure OpenAI RAG Chatbot |
| **주요 목적** | Tibero DB 문서 기반 Q&A |
| **프레임워크** | Streamlit |
| **AI 모델** | Azure OpenAI (GPT-4.1-mini) |
| **검색 인덱스** | Azure AI Search (Vector Index) |

---

## 🧩 주요 기능

- 🔍 **문서 기반 검색 (RAG)**  
  Azure AI Search의 벡터 검색을 통해 관련 기술 문서를 검색합니다.

- 💬 **대화형 질의응답 (Chat Interface)**  
  Streamlit의 채팅 UI를 통해 자연스러운 대화형 질의응답이 가능합니다.

- 📚 **출처 표시**  
  답변에 사용된 문서의 제목 및 링크를 자동으로 표시합니다.

- ⚙️ **설정 조정 (Sidebar)**  
  - 모델 파라미터 (Temperature, Max Tokens)
  - 검색 설정 (검색 문서 수, 관련성 엄격도)
  - 시스템 정보 확인 및 대화 초기화

- 💾 **대화 저장 기능**  
  생성된 대화를 JSON 파일로 다운로드할 수 있습니다.

---

## 🏗️ 시스템 아키텍처

```
사용자
   │
   ▼
Streamlit Chat UI
   │
   ▼
Azure OpenAI (GPT-4.1-mini)
   │      ▲
   ▼      │
Azure AI Search (Vector Index)
   │
   ▼
Tibero 문서 임베딩 데이터
```

---

## ⚙️ 환경 설정

### 1️⃣ 필수 패키지 설치

```bash
pip install streamlit openai python-dotenv
```

### 2️⃣ 환경 변수 설정 (`.env` 파일)

```bash
AZURE_SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net
AZURE_SEARCH_API_KEY=<your-search-api-key>
AZURE_OPENAI_ENDPOINT=https://<your-openai-endpoint>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-openai-api-key>
AZURE_DEPLOYMENT_MODEL=dev-gpt-4.1-mini
AZURE_DEPLOYMENT_EMBEDDING_NAME=text-embedding-3-small
AZURE_SEARCH_INDEX=tibero-vector
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

---

## 🚀 실행 방법

```bash
streamlit run mvp_ktds_kyh_001.py
```

실행 후 브라우저에서 아래 주소로 접속합니다:
```
http://localhost:8501
```

---

## 💡 사용 방법

1. **질문 입력**  
   “Tibero 백업 복구 절차 알려줘” 등의 질문을 입력합니다.

2. **AI 답변 확인**  
   GPT 모델이 검색된 문서를 기반으로 답변을 제공합니다.

3. **참고 문서 열기**  
   답변 하단의 “📚 참고 문서”를 열어 인용 문서를 확인합니다.

4. **대화 저장 (옵션)**  
   “💾 대화 저장” 버튼을 눌러 JSON 파일로 다운로드할 수 있습니다.

---

## 🧱 주요 코드 구조

| 함수 | 설명 |
|------|------|
| `get_chat_client()` | Azure OpenAI 클라이언트 초기화 |
| `create_rag_parameters()` | RAG용 Azure Search 파라미터 생성 |
| `get_answer()` | GPT 모델을 호출해 답변 생성 |
| `display_chat_message()` | 채팅 메시지 UI 렌더링 |
| `initialize_session_state()` | Streamlit 세션 상태 초기화 |
| `reset_conversation()` | 대화 내용 초기화 |
| `main()` | Streamlit 메인 실행 함수 |

---

## 🧠 기술 스택

- **Python 3.10+**
- **Streamlit**
- **Azure OpenAI Service**
- **Azure Cognitive Search**
- **dotenv**

