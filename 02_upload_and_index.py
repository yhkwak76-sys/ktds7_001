#!/usr/bin/env python3
"""
Azure OpenAI RAG - PDF 업로드 및 인덱싱 스크립트
"""

import os
import json
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)
from openai import AzureOpenAI
import PyPDF2

# 환경 변수 로드
load_dotenv()

# Azure 설정
SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER")
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_API_KEY")  # 변경: AZURE_SEARCH_API_KEY
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")  # 변경: AZURE_OPENAI_API_KEY
OPENAI_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT_MODEL")  # 추가: GPT 모델명
EMBEDDING_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT_EMBEDDING_NAME")  # 변경
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# OpenAI 클라이언트 초기화
openai_client = None

def init_openai_client():
    """OpenAI 클라이언트 초기화"""
    global openai_client
    if openai_client is None:
        openai_client = AzureOpenAI(
            azure_endpoint=OPENAI_ENDPOINT,
            api_key=OPENAI_KEY,
            api_version=OPENAI_API_VERSION
        )
    return openai_client


def extract_text_from_pdf(pdf_path: str) -> str:
    """PDF 파일에서 텍스트 추출"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"    총 {total_pages}페이지 읽는 중...", end=" ")
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                
                # 진행 상황 표시
                if page_num % 10 == 0 or page_num == total_pages:
                    print(f"{page_num}/{total_pages}", end=" ")
            
            print("완료!")
    except Exception as e:
        print(f"\n    ❌ PDF 읽기 오류: {e}")
    return text


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """텍스트를 청크로 분할"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # 빈 청크 제외
        if chunk.strip():
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks


def get_embedding(text: str) -> List[float]:
    """텍스트의 임베딩 벡터 생성"""
    try:
        client = init_openai_client()
        response = client.embeddings.create(
            model=EMBEDDING_DEPLOYMENT,
            input=text[:8000]  # 토큰 제한을 위해 텍스트 자르기
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"\n    ⚠️  임베딩 생성 오류: {e}")
        return []


def create_search_index():
    """Azure Cognitive Search 인덱스 생성"""
    print("\n[1/3] 검색 인덱스 생성")
    print("-" * 60)
    
    try:
        index_client = SearchIndexClient(
            endpoint=SEARCH_ENDPOINT,
            credential=AzureKeyCredential(SEARCH_KEY)
        )
        
        # 벡터 검색 설정
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="hnsw-config")
            ],
            profiles=[
                VectorSearchProfile(
                    name="vector-profile",
                    algorithm_configuration_name="hnsw-config"
                )
            ]
        )
        
        # 시맨틱 검색 설정
        semantic_config = SemanticConfiguration(
            name="semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                content_fields=[SemanticField(field_name="content")]
            )
        )
        
        semantic_search = SemanticSearch(
            configurations=[semantic_config]
        )
        
        # 인덱스 필드 정의
        fields = [
            SimpleField(name="id", type="Edm.String", key=True),
            SearchableField(name="title", type="Edm.String"),
            SearchableField(name="content", type="Edm.String"),
            SimpleField(name="source", type="Edm.String", filterable=True),
            SimpleField(name="chunk_id", type="Edm.Int32"),
            SearchField(
                name="content_vector",
                type="Collection(Edm.Single)",
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_profile_name="vector-profile"
            ),
        ]
        
        # 인덱스 생성
        index = SearchIndex(
            name=INDEX_NAME,
            fields=fields,
            vector_search=vector_search,
            semantic_search=semantic_search
        )
        
        result = index_client.create_or_update_index(index)
        print(f"✓ 인덱스 '{INDEX_NAME}' 생성 완료!")
        print(f"  - 벡터 차원: 1536")
        print(f"  - 시맨틱 검색: 활성화")
        
    except Exception as e:
        print(f"❌ 인덱스 생성 오류: {e}")
        raise


def get_blob_service_client():
    """Blob Service Client 생성 (Storage Account Key 사용)"""
    try:
        # DefaultAzureCredential로 인증
        credential = DefaultAzureCredential()
        
        # Storage Management Client 생성
        storage_client = StorageManagementClient(credential, SUBSCRIPTION_ID)
        
        # Storage Account Key 가져오기
        storage_keys = storage_client.storage_accounts.list_keys(
            RESOURCE_GROUP,
            STORAGE_ACCOUNT
        )
        storage_key = storage_keys.keys[0].value
        
        # Blob Service Client 생성 (Account Key 사용)
        blob_service_url = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(
            account_url=blob_service_url,
            credential=storage_key
        )
        
        return blob_service_client
        
    except Exception as e:
        print(f"❌ Blob Service Client 생성 실패: {e}")
        raise


def upload_pdfs_to_blob(data_folder: str = "./data"):
    """로컬 PDF 파일을 Azure Blob Storage에 업로드"""
    print("\n[2/3] PDF 파일 업로드")
    print("-" * 60)
    
    try:
        blob_service_client = get_blob_service_client()
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        # 컨테이너 확인 및 생성
        if not container_client.exists():
            container_client.create_container()
            print(f"✓ 컨테이너 '{CONTAINER_NAME}' 생성 완료")
        else:
            print(f"✓ 컨테이너 '{CONTAINER_NAME}' 확인 완료")
        
        # PDF 파일 찾기
        pdf_files = list(Path(data_folder).glob("*.pdf"))
        
        if not pdf_files:
            print(f"⚠️  '{data_folder}' 폴더에 PDF 파일이 없습니다.")
            return []
        
        print(f"\n업로드할 파일: {len(pdf_files)}개")
        
        uploaded_files = []
        for i, pdf_file in enumerate(pdf_files, 1):
            blob_name = pdf_file.name
            file_size_mb = pdf_file.stat().st_size / (1024 * 1024)
            
            print(f"\n  [{i}/{len(pdf_files)}] {blob_name} ({file_size_mb:.2f} MB)")
            
            try:
                blob_client = blob_service_client.get_blob_client(
                    container=CONTAINER_NAME,
                    blob=blob_name
                )
                
                with open(pdf_file, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True)
                
                print(f"    ✓ 업로드 완료")
                uploaded_files.append(str(pdf_file))
                
            except Exception as e:
                print(f"    ❌ 업로드 실패: {e}")
        
        print(f"\n✓ {len(uploaded_files)}/{len(pdf_files)}개 파일 업로드 완료!")
        return uploaded_files
        
    except Exception as e:
        print(f"❌ 업로드 중 오류 발생: {e}")
        raise


def index_documents(data_folder: str = "./data"):
    """PDF 문서를 읽고 Azure Cognitive Search에 인덱싱"""
    print("\n[3/3] PDF 문서 인덱싱")
    print("-" * 60)
    
    try:
        search_client = SearchClient(
            endpoint=SEARCH_ENDPOINT,
            index_name=INDEX_NAME,
            credential=AzureKeyCredential(SEARCH_KEY)
        )
        
        pdf_files = list(Path(data_folder).glob("*.pdf"))
        
        if not pdf_files:
            print(f"⚠️  '{data_folder}' 폴더에 PDF 파일이 없습니다.")
            return
        
        print(f"\n인덱싱할 파일: {len(pdf_files)}개\n")
        
        total_documents = 0
        total_chunks = 0
        
        for file_idx, pdf_file in enumerate(pdf_files, 1):
            print(f"[{file_idx}/{len(pdf_files)}] 처리 중: {pdf_file.name}")
            
            # 1. PDF 텍스트 추출
            text = extract_text_from_pdf(str(pdf_file))
            if not text.strip():
                print(f"    ⚠️  텍스트를 추출할 수 없습니다. 스킵합니다.")
                continue
            
            print(f"    추출된 텍스트: {len(text):,}자")
            
            # 2. 텍스트 청크 분할
            chunks = chunk_text(text)
            total_chunks += len(chunks)
            print(f"    생성된 청크: {len(chunks)}개")
            
            # 3. 임베딩 생성 및 인덱싱
            documents = []
            print(f"    임베딩 생성 중...", end=" ")
            
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                
                # 임베딩 생성
                embedding = get_embedding(chunk)
                if not embedding:
                    continue
                
                doc_id = f"{pdf_file.stem}_{i}"
                document = {
                    "id": doc_id,
                    "title": pdf_file.stem,
                    "content": chunk,
                    "source": pdf_file.name,
                    "chunk_id": i,
                    "content_vector": embedding
                }
                
                documents.append(document)
                
                # 진행 상황 표시
                if (i + 1) % 10 == 0 or (i + 1) == len(chunks):
                    print(f"{i + 1}/{len(chunks)}", end=" ")
                
                # 배치로 업로드 (50개씩)
                if len(documents) >= 50:
                    try:
                        search_client.upload_documents(documents=documents)
                        total_documents += len(documents)
                        documents = []
                    except Exception as e:
                        print(f"\n    ⚠️  인덱싱 오류: {e}")
            
            # 남은 문서 업로드
            if documents:
                try:
                    search_client.upload_documents(documents=documents)
                    total_documents += len(documents)
                    print("\n    ✓ 인덱싱 완료")
                except Exception as e:
                    print(f"\n    ⚠️  인덱싱 오류: {e}")
            else:
                print("완료")
            
            print()
        
        print("-" * 60)
        print(f"✓ 인덱싱 완료!")
        print(f"  - 처리된 파일: {len(pdf_files)}개")
        print(f"  - 생성된 청크: {total_chunks}개")
        print(f"  - 인덱싱된 문서: {total_documents}개")
        
    except Exception as e:
        print(f"❌ 인덱싱 중 오류 발생: {e}")
        raise


def verify_environment():
    """환경 변수 확인"""
    print("환경 변수 확인 중...")
    print("-" * 60)
    
    required_vars = {
        "AZURE_SUBSCRIPTION_ID": SUBSCRIPTION_ID,
        "AZURE_RESOURCE_GROUP": RESOURCE_GROUP,
        "AZURE_STORAGE_ACCOUNT": STORAGE_ACCOUNT,
        "AZURE_STORAGE_CONTAINER": CONTAINER_NAME,
        "AZURE_SEARCH_ENDPOINT": SEARCH_ENDPOINT,
        "AZURE_SEARCH_API_KEY": SEARCH_KEY,
        "AZURE_SEARCH_INDEX": INDEX_NAME,
        "AZURE_OPENAI_ENDPOINT": OPENAI_ENDPOINT,
        "AZURE_OPENAI_API_KEY": OPENAI_KEY,
        "AZURE_DEPLOYMENT_MODEL": OPENAI_DEPLOYMENT,
        "AZURE_DEPLOYMENT_EMBEDDING_NAME": EMBEDDING_DEPLOYMENT,
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        print("\n❌ 다음 환경 변수가 설정되지 않았습니다:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\n.env 파일을 확인하거나 setup-azure-rag.sh를 먼저 실행하세요.")
        return False
    
    print("✓ 모든 환경 변수 확인 완료")
    print(f"  - Storage Account: {STORAGE_ACCOUNT}")
    print(f"  - Container: {CONTAINER_NAME}")
    print(f"  - Search Index: {INDEX_NAME}")
    print(f"  - Embedding Model: {EMBEDDING_DEPLOYMENT}")
    return True


def main():
    """메인 실행 함수"""
    print("\n" + "=" * 60)
    print("Azure OpenAI RAG - PDF 업로드 및 인덱싱")
    print("=" * 60)
    
    # 환경 변수 확인
    if not verify_environment():
        return
    
    try:
        # 1. 검색 인덱스 생성
        create_search_index()
        
        # 2. PDF 파일을 Blob Storage에 업로드
        upload_pdfs_to_blob()
        
        # 3. PDF 문서 인덱싱
        index_documents()
        
        # 완료 메시지
        print("\n" + "=" * 60)
        print("✅ 모든 작업 완료!")
        print("=" * 60)
        print("\n다음 단계:")
        print("  python query.py")
        print("\n위 명령어로 질의응답을 시작할 수 있습니다.")
        print("=" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n작업이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        print("\n문제가 계속되면 다음을 확인하세요:")
        print("  1. Azure 로그인 상태: az account show")
        print("  2. 환경 변수 설정: .env 파일 확인")
        print("  3. 리소스 생성 여부: Azure Portal 확인")


if __name__ == "__main__":
    main()