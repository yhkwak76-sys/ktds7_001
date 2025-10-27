import streamlit as st
from openai import AzureOpenAI
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType
)
import io
import hashlib
from datetime import datetime

# ========================================
# 1. 페이지 설정
# ========================================
st.set_page_config(
    page_title="Tibero 문서 분석 시스템",
    page_icon="📄",
    layout="wide"
)

st.title("🔍 Tibero 기술문서 자동 요약 및 오류 분석")
st.markdown("---")

# ========================================
# 2. Azure 설정 (사이드바)
# ========================================
with st.sidebar:
    st.header("⚙️ Azure 설정")
    
    # Azure OpenAI 설정
    st.subheader("🤖 Azure OpenAI")
    azure_openai_endpoint = st.text_input(
        "OpenAI Endpoint",
        value="",
        placeholder="https://your-openai.openai.azure.com/",
        help="AZURE_OPENAI_ENDPOINT"
    )
    
    azure_openai_api_key = st.text_input(
        "OpenAI API Key",
        value="",
        type="password",
        placeholder="OpenAI API 키를 입력하세요",
        help="AZURE_OPENAI_API_KEY"
    )
    
    azure_deployment_model = st.text_input(
        "Deployment Model",
        value="dev-gpt-4.1-mini",
        help="AZURE_DEPLOYMENT_MODEL"
    )
    
    st.markdown("---")
    
    # Azure AI Foundry (Document Intelligence) 설정
    st.subheader("📄 Azure AI Foundry")
    azure_doc_intelligence_endpoint = st.text_input(
        "Document Intelligence Endpoint",
        value="",
        placeholder="https://your-doc-intel.cognitiveservices.azure.com/",
        help="AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"
    )
    
    azure_doc_intelligence_key = st.text_input(
        "Document Intelligence Key",
        value="",
        type="password",
        placeholder="Document Intelligence 키를 입력하세요",
        help="AZURE_DOCUMENT_INTELLIGENCE_KEY"
    )
    
    st.markdown("---")
    
    # Azure Search 설정
    st.subheader("🔍 Azure AI Search")
    azure_search_endpoint = st.text_input(
        "Search Endpoint",
        value="",
        placeholder="https://your-search.search.windows.net",
        help="AZURE_SEARCH_ENDPOINT"
    )
    
    azure_search_api_key = st.text_input(
        "Search API Key",
        value="",
        type="password",
        placeholder="Search API 키를 입력하세요",
        help="AZURE_SEARCH_API_KEY"
    )
    
    azure_search_index_name = st.text_input(
        "Search Index Name",
        value="tibero-docs-index",
        help="문서를 저장할 인덱스 이름"
    )
    
    st.markdown("---")
    st.caption("💡 Azure Portal에서 키 정보를 확인하세요")
    
    # 설정 확인 상태
    if azure_openai_endpoint and azure_openai_api_key:
        st.success("✅ OpenAI 설정 완료")
    if azure_doc_intelligence_endpoint and azure_doc_intelligence_key:
        st.success("✅ Document Intelligence 설정 완료")
    if azure_search_endpoint and azure_search_api_key:
        st.success("✅ Search 설정 완료")

# ========================================
# 3. Azure Document Intelligence로 PDF 텍스트 추출
# ========================================
def extract_text_from_pdf_with_azure(pdf_file, endpoint, key):
    """Azure Document Intelligence를 사용해 PDF에서 텍스트를 추출하는 함수"""
    try:
        # Document Intelligence 클라이언트 생성
        client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        
        # PDF 파일을 바이트로 읽기
        pdf_bytes = pdf_file.read()
        
        # Document Intelligence로 분석 (prebuilt-read 모델 사용)
        poller = client.begin_analyze_document(
            model_id="prebuilt-read",
            analyze_request=pdf_bytes,
            content_type="application/pdf"
        )
        
        # 결과 대기
        result = poller.result()
        
        # 텍스트 추출
        text = ""
        if result.content:
            text = result.content
        
        return text
    
    except Exception as e:
        st.error(f"PDF 읽기 오류 (Azure Document Intelligence): {str(e)}")
        return None

# ========================================
# 3-1. Azure Search 인덱스 생성/확인
# ========================================
def create_or_get_search_index(endpoint, key, index_name):
    """Azure Search 인덱스를 생성하거나 기존 인덱스를 가져오는 함수"""
    try:
        # Search Index 클라이언트 생성
        index_client = SearchIndexClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        
        # 인덱스 정의
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="filename", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="ko.lucene"),
            SearchableField(name="keyword", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="upload_date", type=SearchFieldDataType.DateTimeOffset, filterable=True),
            SimpleField(name="file_hash", type=SearchFieldDataType.String, filterable=True)
        ]
        
        index = SearchIndex(name=index_name, fields=fields)
        
        # 인덱스 생성 (이미 존재하면 무시)
        index_client.create_or_update_index(index)
        
        return True
    
    except Exception as e:
        st.error(f"인덱스 생성 오류: {str(e)}")
        return False

# ========================================
# 3-2. Azure Search에 문서 업로드
# ========================================
def upload_to_search(endpoint, key, index_name, filename, content, keyword):
    """추출된 문서를 Azure Search에 업로드하는 함수"""
    try:
        # Search 클라이언트 생성
        search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(key)
        )
        
        # 문서 ID 생성 (파일명 + 타임스탬프 해시)
        file_hash = hashlib.md5(f"{filename}{datetime.now()}".encode()).hexdigest()
        
        # 문서 데이터
        document = {
            "id": file_hash,
            "filename": filename,
            "content": content[:50000],  # Search 제한에 맞춰 50KB로 제한
            "keyword": keyword,
            "upload_date": datetime.utcnow().isoformat() + "Z",
            "file_hash": file_hash
        }
        
        # 문서 업로드
        result = search_client.upload_documents(documents=[document])
        
        return True, file_hash
    
    except Exception as e:
        st.error(f"문서 업로드 오류: {str(e)}")
        return False, None

# ========================================
# 3-3. Azure Search에서 문서 검색
# ========================================
def search_documents(endpoint, key, index_name, query, top=5):
    """Azure Search에서 관련 문서를 검색하는 함수"""
    try:
        # Search 클라이언트 생성
        search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(key)
        )
        
        # 검색 실행
        results = search_client.search(
            search_text=query,
            top=top,
            select=["filename", "content", "keyword", "upload_date"]
        )
        
        # 결과 리스트로 변환
        documents = []
        for result in results:
            documents.append({
                "filename": result.get("filename", ""),
                "content": result.get("content", "")[:500],  # 미리보기용 500자
                "keyword": result.get("keyword", ""),
                "score": result.get("@search.score", 0)
            })
        
        return documents
    
    except Exception as e:
        st.error(f"검색 오류: {str(e)}")
        return []

# ========================================
# 4. Azure OpenAI로 문서 분석 함수
# ========================================
def analyze_document(text, keyword, azure_openai_endpoint, azure_openai_api_key, azure_deployment_model):
    """Azure OpenAI를 사용해 문서를 분석하는 함수"""
    
    # Azure OpenAI 클라이언트 생성
    client = AzureOpenAI(
        azure_endpoint=azure_openai_endpoint,
        api_key=azure_openai_api_key,
        api_version="2024-08-01-preview"
    )
    
    # 시스템 프롬프트
    system_prompt = """너는 Tibero 데이터베이스 전문가이자 기술문서 요약 AI야. 
입력된 Tibero 기술문서나 오류 로그를 분석해서 다음을 생성해:

1. **요약** (핵심 구조, 개념, 절차)
2. **오류/에러코드 분석** (원인, 조치, 관련 매뉴얼 섹션)
3. **추가 확인 필요사항** 2가지
4. **확신도** (높음/중간/낮음)

명확하고 구조화된 형식으로 답변해줘."""

    # 사용자 프롬프트
    user_prompt = f"""다음 Tibero 문서에서 '{keyword}' 관련 내용을 분석해줘:

{text[:4000]}

위 내용을 바탕으로 요약, 오류 분석, 추가 확인사항을 제공해줘."""

    try:
        # API 호출
        response = client.chat.completions.create(
            model=azure_deployment_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        st.error(f"분석 오류: {str(e)}")
        return None

# ========================================
# 5. 메인 화면
# ========================================

# PDF 파일 업로드
uploaded_file = st.file_uploader(
    "📁 Tibero 기술문서 (PDF) 업로드",
    type=['pdf'],
    help="분석할 PDF 파일을 선택하세요"
)

# 키워드 입력
keyword = st.text_input(
    "🔎 검색 키워드",
    placeholder="예: TBR-12170, timeout, listener 등",
    help="문서에서 찾고 싶은 키워드를 입력하세요"
)

# 분석 버튼
analyze_button = st.button("🚀 분석 시작", type="primary", use_container_width=True)

# Azure Search 검색 섹션
st.markdown("---")
st.subheader("🔍 저장된 문서 검색")

col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input(
        "저장된 문서에서 검색",
        placeholder="예: TBR-12170, timeout, listener",
        help="Azure Search에 저장된 문서를 검색합니다"
    )
with col2:
    search_button = st.button("🔎 검색", use_container_width=True)

# 검색 실행
if search_button and search_query:
    if not azure_search_endpoint or not azure_search_api_key:
        st.warning("⚠️ Azure Search 설정을 완료해주세요.")
    else:
        with st.spinner("🔍 문서 검색 중..."):
            search_results = search_documents(
                azure_search_endpoint,
                azure_search_api_key,
                azure_search_index_name,
                search_query,
                top=5
            )
        
        if search_results:
            st.success(f"✅ {len(search_results)}개의 관련 문서를 찾았습니다")
            
            for idx, doc in enumerate(search_results, 1):
                with st.expander(f"📄 {idx}. {doc['filename']} (관련도: {doc['score']:.2f})"):
                    st.markdown(f"**키워드:** {doc['keyword']}")
                    st.markdown("**내용 미리보기:**")
                    st.text(doc['content'][:300] + "...")
        else:
            st.info("검색 결과가 없습니다. 먼저 문서를 업로드하고 분석해주세요.")

st.markdown("---")

# ========================================
# 6. 분석 실행
# ========================================
if analyze_button:
    # 입력 검증
    if not uploaded_file:
        st.warning("⚠️ PDF 파일을 업로드해주세요.")
    elif not keyword:
        st.warning("⚠️ 검색 키워드를 입력해주세요.")
    elif not azure_openai_endpoint or not azure_openai_api_key:
        st.warning("⚠️ Azure OpenAI 설정을 완료해주세요.")
    elif not azure_doc_intelligence_endpoint or not azure_doc_intelligence_key:
        st.warning("⚠️ Azure Document Intelligence 설정을 완료해주세요.")
    else:
        # 분석 진행
        with st.spinner("📄 Azure AI Foundry로 PDF 분석 중... (약 5-10초)"):
            pdf_text = extract_text_from_pdf_with_azure(
                uploaded_file,
                azure_doc_intelligence_endpoint,
                azure_doc_intelligence_key
            )
        
        if pdf_text:
            st.success(f"✅ PDF 텍스트 추출 완료 (총 {len(pdf_text)} 자)")
            
            # Azure Search에 문서 업로드 (선택적)
            if azure_search_endpoint and azure_search_api_key:
                with st.spinner("💾 Azure Search에 문서 저장 중..."):
                    # 인덱스 생성/확인
                    index_created = create_or_get_search_index(
                        azure_search_endpoint,
                        azure_search_api_key,
                        azure_search_index_name
                    )
                    
                    if index_created:
                        # 문서 업로드
                        upload_success, file_hash = upload_to_search(
                            azure_search_endpoint,
                            azure_search_api_key,
                            azure_search_index_name,
                            uploaded_file.name,
                            pdf_text,
                            keyword
                        )
                        
                        if upload_success:
                            st.success(f"✅ 문서가 Azure Search에 저장되었습니다 (ID: {file_hash[:8]}...)")
                        else:
                            st.warning("⚠️ Azure Search 업로드 실패 (분석은 계속 진행됩니다)")
            
            # 추출된 텍스트 미리보기 (선택적)
            with st.expander("📝 추출된 텍스트 미리보기 (처음 500자)"):
                st.text(pdf_text[:500] + "...")
            
            with st.spinner("🤖 AI 분석 중... (약 10-20초 소요)"):
                result = analyze_document(
                    pdf_text,
                    keyword,
                    azure_openai_endpoint,
                    azure_openai_api_key,
                    azure_deployment_model
                )
            
            if result:
                st.markdown("## 📊 분석 결과")
                st.markdown(result)
                
                # 다운로드 버튼
                st.download_button(
                    label="💾 결과 다운로드 (TXT)",
                    data=result,
                    file_name=f"tibero_analysis_{keyword}.txt",
                    mime="text/plain"
                )

# ========================================
# 7. 사용 예시 (하단)
# ========================================
with st.expander("💡 사용 예시"):
    st.markdown("""
    ### 입력 예시
    ```
    TBR-12170: Timeout occurred while waiting for a response from the server. 
    This error may indicate that the server is not reachable or network latency is high. 
    Check listener configuration and firewall rules.
    ```
    
    ### 출력 예시
    ```
    요약: 서버 응답 대기 중 타임아웃 발생. 네트워크 지연 혹은 리스너 설정 문제 가능.
    
    오류 분석:
    * 원인: (1) 서버 비가동 또는 리스너 비활성화 
            (2) 방화벽 포트 차단 
            (3) 네트워크 지연
    * 조치: listener.ora 확인, ping 테스트, 방화벽 8629 포트 허용
    * 참고: Tibero Admin Guide 3.4절
    
    추가 확인 필요: DB Listener 상태, OS 방화벽 정책
    
    확신도: 높음
    ```
    """)

# ========================================
# 8. 푸터
# ========================================
st.markdown("---")
st.caption("🔧 Tibero 기술문서 자동 요약 및 오류 분석 시스템 v1.0")
