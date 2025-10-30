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


# 🤖 Azure OpenAI RAG Chatbot (기술 문서 검색)

이 프로젝트는 **Azure OpenAI**와 **Azure AI Search**를 활용한  
**검색 기반 질의응답 시스템 (RAG: Retrieval-Augmented Generation)**입니다.  
Azure OpenAI, Cognitive Search, Blob Storage를 활용하여 PDF 매뉴얼을 인덱싱하고, Streamlit 웹 인터페이스를 통해 자연어로 질의응답을 수행합니다.

---

## 📚 참고 문서 (Data Source)

본 프로젝트는 다음 Tibero 7 공식 문서를 기반으로 학습 및 검색 인덱싱합니다.

| 문서명 | 설명 |
|--------|------|
| `Tibero_7_Error-Reference-Guide.pdf` | 에러 코드별 원인 및 조치 가이드 |
| `Tibero_7_Glossary-Guide.pdf` | Tibero 용어집 및 주요 개념 정의 |
| `Tibero_7_JDBC-Development-Guide.pdf` | JDBC 프로그래밍 및 연결 설정 가이드 |
| `Tibero_7_전환 유틸리티 가이드.pdf` | 오라클 → Tibero 전환 도구 및 절차 설명 |

---

## 🏗️ 시스템 구성

```mermaid
flowchart TD
    A[📄 PDF 문서] -->|Upload| B[☁️ Azure Blob Storage]
    B -->|Extract + Chunk + Embed| C[🔍 Azure AI Search Index]
    C -->|Vector Query| D[🤖 Azure OpenAI (GPT-4)]
    D -->|Response| E[💬 Streamlit Chat UI]
```

---

## ⚙️ 주요 구성 파일

| 파일명 | 역할 |
|--------|------|
| `.env` | Azure 구독/리소스/엔드포인트 설정 |
| `01_storage_and_upload.py` | Blob Storage 생성 및 PDF 업로드 스크립트 |
| `02_upload_and_index.py` | PDF → 텍스트 추출, 임베딩 생성, 인덱싱 자동화 |
| `mvp_ktds_kyh_001.py` | Streamlit 기반 Tibero Q&A 챗봇 UI |

---

## 🧩 환경 변수 설정 (`.env`)

```bash
# Azure Subscription
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_RESOURCE_GROUP=pro-kyh-rg
AZURE_LOCATION=francecentral

# Azure Storage
AZURE_STORAGE_ACCOUNT=prokyhstorage20251029
AZURE_STORAGE_CONTAINER=tibero-docs

# Azure Cognitive Search
AZURE_SEARCH_ENDPOINT=https://pro-kyh-ai-search-001.search.windows.net
AZURE_SEARCH_API_KEY=<your-search-api-key>
AZURE_SEARCH_INDEX=tibero-index

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://pro-kyh-openai-001.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-openai-api-key>
AZURE_DEPLOYMENT_MODEL=dev-gpt-4.1-mini
AZURE_DEPLOYMENT_EMBEDDING_NAME=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

---

## 🚀 실행 절차

### 1️⃣ 의존성 설치

```bash
pip install -r requirements.txt
```

> 주요 패키지:
> - `azure-storage-blob`
> - `azure-search-documents`
> - `azure-identity`
> - `openai`
> - `streamlit`
> - `PyPDF2`
> - `python-dotenv`

---

### 2️⃣ Blob Storage 업로드

```bash
python 01_storage_and_upload.py
```
- 지정된 PDF 파일 또는 폴더 내 모든 PDF를 Azure Blob에 업로드합니다.

---

### 3️⃣ PDF 인덱싱 및 임베딩 생성

```bash
python 02_upload_and_index.py
```
- PDF 텍스트를 추출하고, 1,000자 단위 청크로 분할하여 Azure OpenAI 임베딩 생성 후 Search Index에 업로드합니다.

---

### 4️⃣ Streamlit 챗봇 실행

```bash
streamlit run mvp_ktds_kyh_001.py
```
- 브라우저에서 `http://localhost:8501` 접속  
- Tibero 관련 질문을 자연어로 입력하면, 관련 문서를 기반으로 답변 생성

---

## 💬 예시 질의

| 질문 | 예시 답변 요약 |
|------|----------------|
| “Tibero에서 ORA-00942에 해당하는 오류는?” | `TBSQL-xxxxx` 오류 코드와 해결 방법 설명 |
| “JDBC 연결 설정 시 필요한 URL 형식은?” | `jdbc:tibero:thin:@host:port:database` 형식 안내 |
| “Tibero 전환 도구에서 스키마 매핑 방법은?” | 전환 유틸리티 가이드의 매핑 설정 절차 요약 |

---

## 🧠 구조 요약

- **Vector 기반 검색 (text-embedding-3-small)**
- **Semantic Search 활성화**
- **GPT-4.1-mini** 모델로 RAG 응답
- **Azure Search + Blob + OpenAI 통합 파이프라인**

---

## 📈 향후 확장 방향

- 🔍 질의 로그 기반 검색 품질 개선
- 🧩 추가 Tibero 매뉴얼 자동 인덱싱
- 🌐 Azure Functions를 통한 주기적 업데이트
- 💬 관리자용 문서 업로드/삭제 UI 추가

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

## 👨‍💻 개발 환경

- Python 3.11+
- Azure SDK for Python
- Streamlit 1.38+
- Windows 10/11 (테스트 환경)
- Visual Studio Code / GitHub

