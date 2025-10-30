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


# Azure OpenAI RAG Chatbot (기술 문서 검색)

이 프로젝트는 **Azure OpenAI**와 **Azure AI Search**를 활용한  
**검색 기반 질의응답 시스템 (RAG: Retrieval-Augmented Generation)**입니다.  
Azure OpenAI, Azure AI Search, Blob Storage를 활용하여 PDF 매뉴얼을 인덱싱하고, Streamlit 웹 인터페이스를 통해 자연어로 질의응답을 수행합니다.

---

# 🤖 AI 기반 기술문서 자동 요약 및 오류 분석 시스템

Azure OpenAI와 Azure AI Search를 활용한 Tibero 데이터베이스 기술문서 검색 및 질의응답 챗봇입니다.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Azure](https://img.shields.io/badge/Azure-OpenAI-0078D4.svg)

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [시스템 아키텍처](#-시스템-아키텍처)
- [설치 방법](#-설치-방법)
- [문서 인덱싱 프로세스](#-문서-인덱싱-프로세스)
- [사용 방법](#-사용-방법)
- [프로젝트 구조](#-프로젝트-구조)
- [주요 기능 상세](#-주요-기능-상세)

## 🎯 프로젝트 개요

이 프로젝트는 Tibero 데이터베이스 관련 기술문서, 로그, 매뉴얼을 AI가 자동으로 분석하여 다음을 제공합니다:

- ✅ 핵심 개념 자동 요약
- ✅ 주요 오류 원인 설명
- ✅ 문제 해결 가이드 생성
- ✅ 실시간 질의응답

## ✨ 주요 기능

### 1. 지능형 문서 검색 (RAG)
- **벡터 검색**: Azure AI Search를 통한 의미론적 문서 검색
- **문맥 기반 답변**: 검색된 문서를 바탕으로 정확한 답변 생성
- **인용 출처 표시**: 답변의 근거가 된 문서 출처 자동 표시

### 2. 대화형 인터페이스
- **실시간 채팅**: Streamlit 기반 직관적인 웹 UI
- **대화 히스토리**: 이전 대화 내용 유지 및 참조
- **타임스탬프**: 각 메시지의 시간 기록

### 3. 고급 설정
- **Temperature 조절**: 답변의 창의성 수준 조정 (0.0 ~ 1.0)
- **Max Tokens**: 생성할 답변의 최대 길이 설정
- **검색 문서 수**: 참조할 문서 개수 조정 (1 ~ 10)
- **관련성 엄격도**: 문서 관련성 필터링 강도 조정 (1 ~ 5)

### 4. 대화 관리
- **초기화**: 대화 내용 전체 삭제
- **통계 확인**: 메시지 개수 확인
- **대화 저장**: JSON 형식으로 대화 내용 다운로드

## 🛠 기술 스택

### AI & Cloud
- **Azure OpenAI**: GPT 모델 기반 답변 생성
- **Azure AI Search**: 벡터 검색 및 인덱싱
- **Azure Storage Account**: 문서 저장 (Blob Storage)

### Backend
- **Python 3.8+**: 메인 프로그래밍 언어
- **OpenAI Python SDK**: Azure OpenAI API 연동
- **python-dotenv**: 환경 변수 관리

### Frontend
- **Streamlit**: 웹 인터페이스 프레임워크

### Document Processing
- **PDF 처리**: PDF 텍스트 추출
- **Chunking**: 1,000자 단위 분할 (200자 오버랩)
- **Embedding**: Azure OpenAI 임베딩 모델 (text-embedding-3-small)

## 🏗 시스템 아키텍처

```
┌─────────────────┐
│   사용자 입력    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Streamlit UI   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Azure OpenAI   │◄──── RAG 파라미터
│   (GPT Model)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Azure AI Search │
│  (벡터 검색)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Blob Storage    │
│ (PDF 문서)      │
└─────────────────┘
```

### 데이터 흐름

1. **사용자 질문 입력** → Streamlit UI
2. **임베딩 생성** → Azure OpenAI Embedding Model
3. **벡터 검색** → Azure AI Search에서 관련 문서 검색
4. **답변 생성** → Azure OpenAI GPT 모델이 검색된 문서 기반으로 답변
5. **결과 표시** → Streamlit UI에 답변 및 출처 표시

## 📦 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Python 가상환경 생성
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### 필수 패키지 목록 (requirements.txt)
```txt
# Azure SDK
azure-identity
azure-mgmt-storage
azure-storage-blob
azure-search-documents

# OpenAI & PDF
openai

# Web Framework
streamlit

# 환경 변수
python-dotenv
```



## 📚 문서 인덱싱 프로세스

애플리케이션 실행 전에 문서를 Azure AI Search에 인덱싱해야 합니다.

### 1단계: 스토리지 설정 및 PDF 업로드
```bash
python 01_storage_and_upload.py
```
- Azure Storage Account 컨테이너 생성
- Tibero 기술문서 PDF를 Blob Storage에 업로드

### 2단계: 문서 인덱싱
```bash
python 02_upload_and_index.py
```
- PDF에서 텍스트 추출
- 1,000자 단위로 청킹 (200자 오버랩)
- Azure OpenAI로 임베딩 생성
- 50개 배치 단위로 Azure AI Search 인덱스에 업로드

## 🚀 사용 방법

### 애플리케이션 실행

**방법 1: Python 직접 실행**
```bash
streamlit run mvp_ktds_kyh_001.py
```

**방법 2: 쉘 스크립트 실행**
```bash
chmod +x streamlit.sh  # 실행 권한 부여 (최초 1회)
./streamlit.sh
```

브라우저에서 자동으로 `http://localhost:8501` 로 접속됩니다.

### 기본 사용법

1. **질문 입력**: 하단 채팅 입력창에 질문 입력
2. **답변 확인**: AI가 생성한 답변 및 참고 문서 확인
3. **설정 조정**: 좌측 사이드바에서 모델 파라미터 조정
4. **대화 관리**: 대화 초기화, 통계 확인, 대화 저장

### 설정 가이드

#### Temperature (창의성)
- **0.0 ~ 0.3**: 정확하고 일관된 답변 (기술 문서용)
- **0.4 ~ 0.7**: 균형잡힌 답변 (기본값)
- **0.8 ~ 1.0**: 창의적이고 다양한 답변

#### Max Tokens (최대 길이)
- **100 ~ 500**: 짧은 답변
- **500 ~ 1000**: 중간 길이 답변 (기본값)
- **1000 ~ 2000**: 상세한 긴 답변

#### 검색 문서 수
- **1 ~ 3**: 빠른 검색, 핵심 문서만
- **4 ~ 6**: 균형잡힌 검색 (기본값: 5)
- **7 ~ 10**: 광범위한 검색, 더 많은 참고 자료

#### 관련성 엄격도
- **1 ~ 2**: 느슨한 필터링, 더 많은 문서 포함
- **3**: 균형잡힌 필터링 (기본값)
- **4 ~ 5**: 엄격한 필터링, 관련성 높은 문서만

## 📁 프로젝트 구조

```
project/
├── data/                         # 데이터 폴더
├── .deployment                   # 배포 설정 파일
├── .env                          # 환경 변수
├── 01_storage_and_upload.py      # 스토리지 및 업로드 스크립트
├── 02_upload_and_index.py        # 문서 업로드 및 인덱싱 스크립트
├── 03_chat_001.py                # 챗봇 초기 버전
├── mvp_ktds_kyh_001.py           # 메인 Streamlit 애플리케이션
├── README.md                     # 프로젝트 문서 (이 파일)
├── requirements.txt              # Python 의존성 패키지
└── streamlit.sh                  # Streamlit 실행 스크립트
```

### 파일 설명

- **01_storage_and_upload.py**: Azure Storage Account 설정 및 PDF 파일 업로드
- **02_upload_and_index.py**: PDF 문서를 읽어서 텍스트 추출, 청킹, 임베딩 생성 후 Azure AI Search 인덱스에 업로드
- **03_chat_001.py**: 챗봇 초기 개발 버전
- **mvp_ktds_kyh_001.py**: 최종 Streamlit 기반 RAG 챗봇 웹 애플리케이션
- **streamlit.sh**: Streamlit 애플리케이션 실행을 위한 쉘 스크립트

## 🔧 주요 기능 상세

### 1. 세션 상태 관리

```python
initialize_session_state()
- messages: 대화 메시지 배열 (시스템 + 사용자 + 어시스턴트)
- chat_history: UI 표시용 채팅 히스토리
- chat_client: Azure OpenAI 클라이언트 (캐시)
- message_counter: 메시지 고유 ID 카운터
```

### 2. RAG 파라미터

```python
create_rag_parameters(top_n=5, strictness=3)
- 검색 타입: vector (의미론적 검색)
- 임베딩: text-embedding-3-small 모델 사용
- top_n_documents: 검색할 문서 개수
- strictness: 관련성 필터링 강도
```

### 3. 답변 생성 프로세스

```python
get_answer()
1. 사용자 메시지를 대화 배열에 추가
2. RAG 파라미터와 함께 Azure OpenAI API 호출
3. 답변 및 인용 정보 추출
4. 어시스턴트 메시지를 대화 배열에 추가
5. 오류 처리
```

### 4. 인용 중복 제거

```python
remove_duplicate_citations()
- 제목 기준으로 중복 인용 제거
- 사용자에게 깔끔한 참고 문서 목록 제공
```

## 💡 사용 예시

### 질문 예시

```
Q: Tibero에서 테이블 생성 방법을 알려주세요.

A: Tibero에서 테이블을 생성하는 기본 구문은 다음과 같습니다:

CREATE TABLE 테이블명 (
    컬럼명1 데이터타입 [제약조건],
    컬럼명2 데이터타입 [제약조건],
    ...
);

예를 들어, 사원 테이블을 생성한다면:

CREATE TABLE EMPLOYEE (
    EMP_ID NUMBER(6) PRIMARY KEY,
    EMP_NAME VARCHAR2(50) NOT NULL,
    HIRE_DATE DATE DEFAULT SYSDATE
);

[참고 문서: Tibero SQL Reference Guide]
```

### 오류 분석 예시

```
Q: ORA-01017 오류가 발생했습니다. 원인과 해결 방법을 알려주세요.

A: ORA-01017 오류는 "invalid username/password" 오류입니다.

원인:
1. 잘못된 사용자명 또는 비밀번호
2. 계정 잠김 상태
3. 비밀번호 만료

해결 방법:
1. 사용자명과 비밀번호 재확인
2. 계정 상태 확인: SELECT * FROM DBA_USERS WHERE USERNAME = '...';
3. 계정 잠김 해제: ALTER USER ... ACCOUNT UNLOCK;
4. 비밀번호 재설정: ALTER USER ... IDENTIFIED BY new_password;

[참고 문서: Tibero Error Messages Manual]
```

## 📊 성능 최적화

### 캐싱
```python
@st.cache_resource
def get_chat_client():
    # Azure OpenAI 클라이언트는 한 번만 생성하고 재사용
```

### 배치 처리
- 문서 인덱싱 시 50개 배치 단위로 처리
- 네트워크 호출 최소화

## 🐛 문제 해결

### 일반적인 오류

#### 1. Azure API 인증 오류
```bash
# API 키와 엔드포인트가 올바른지 확인
# Azure Portal에서 키 재생성
```

#### 2. 검색 결과 없음
```bash
# Azure AI Search 인덱스에 문서가 인덱싱되어 있는지 확인
# 검색 쿼리의 관련성 엄격도를 낮춰보세요 (1~2)
```
