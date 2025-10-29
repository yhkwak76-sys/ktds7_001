import os
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient

# --- 1. 설정 정보 ---
SUBSCRIPTION_ID = "dc6618c1-53d2-4bc8-ab82-68140c3fbde1"
RESOURCE_GROUP_NAME = "pro-kyh-rg"
LOCATION = "francecentral"
CONTAINER_NAME = "tibero-docs"
STORAGE_ACCOUNT_NAME = "prokyhstorage24q19"

# 업로드할 PDF 파일의 경로
# 단일 파일 또는 폴더 지정 가능
PDF_FILE_PATH = "./data/Tibero_7_JDBC-Development-Guide.pdf"
# 전체 폴더 업로드를 원하면 아래 주석 해제
# DATA_FOLDER = "./data"


def get_storage_account_key(credential, subscription_id, resource_group, storage_account):
    """Storage Account Key 가져오기"""
    try:
        storage_client = StorageManagementClient(credential, subscription_id)
        storage_keys = storage_client.storage_accounts.list_keys(
            resource_group, 
            storage_account
        )
        return storage_keys.keys[0].value
    except Exception as e:
        raise Exception(f"Storage Key 가져오기 실패: {e}")


def create_blob_service_client(storage_account, storage_key):
    """Blob Service Client 생성"""
    blob_service_url = f"https://{storage_account}.blob.core.windows.net"
    return BlobServiceClient(account_url=blob_service_url, credential=storage_key)


def ensure_container_exists(blob_service_client, container_name):
    """컨테이너가 없으면 생성"""
    try:
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
            print(f"✓ Blob 컨테이너 '{container_name}' 생성 완료")
        else:
            print(f"✓ Blob 컨테이너 '{container_name}' 확인 완료")
        return container_client
    except Exception as e:
        raise Exception(f"컨테이너 작업 중 오류: {e}")


def upload_single_file(container_client, file_path, blob_name=None):
    """단일 파일 업로드"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
    if blob_name is None:
        blob_name = os.path.basename(file_path)
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"\n업로드 중: {blob_name} ({file_size_mb:.2f} MB)")
    
    blob_client = container_client.get_blob_client(blob_name)
    
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    
    print(f"  ✓ 업로드 완료!")
    return blob_name


def upload_folder(container_client, folder_path, pattern="*.pdf"):
    """폴더의 모든 파일 업로드"""
    folder = Path(folder_path)
    
    if not folder.exists():
        raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {folder_path}")
    
    files = list(folder.glob(pattern))
    
    if not files:
        print(f"⚠️  '{folder_path}' 폴더에 {pattern} 파일이 없습니다.")
        return []
    
    print(f"\n총 {len(files)}개 파일 발견")
    
    uploaded_files = []
    for i, file_path in enumerate(files, 1):
        try:
            print(f"\n[{i}/{len(files)}] {file_path.name}")
            blob_name = upload_single_file(container_client, str(file_path))
            uploaded_files.append(blob_name)
        except Exception as e:
            print(f"  ❌ 업로드 실패: {e}")
    
    return uploaded_files


def list_blobs(container_client):
    """업로드된 파일 목록 출력"""
    print("\n" + "=" * 60)
    print("업로드된 파일 목록:")
    print("-" * 60)
    
    try:
        blobs = list(container_client.list_blobs())
        
        if not blobs:
            print("  (파일 없음)")
            return
        
        total_size = 0
        for blob in blobs:
            size_kb = blob.size / 1024
            total_size += blob.size
            print(f"  • {blob.name} ({size_kb:.2f} KB)")
        
        print("-" * 60)
        print(f"총 {len(blobs)}개 파일, {total_size / (1024 * 1024):.2f} MB")
        
    except Exception as e:
        print(f"파일 목록 조회 실패: {e}")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Azure Storage PDF 업로드")
    print("=" * 60)
    print(f"\nStorage Account: {STORAGE_ACCOUNT_NAME}")
    print(f"Container: {CONTAINER_NAME}")
    print(f"Region: {LOCATION}\n")
    
    try:
        # 1. Azure 인증
        print("[1/5] Azure 자격 증명 설정...")
        credential = DefaultAzureCredential()
        print("  ✓ 자격 증명 설정 완료")
        
        # 2. Storage Account Key 가져오기
        print("\n[2/5] Storage Account Key 가져오기...")
        storage_key = get_storage_account_key(
            credential, 
            SUBSCRIPTION_ID, 
            RESOURCE_GROUP_NAME, 
            STORAGE_ACCOUNT_NAME
        )
        print("  ✓ Storage Key 획득 완료")
        
        # 3. Blob Service Client 생성
        print("\n[3/5] Blob Service Client 생성...")
        blob_service_client = create_blob_service_client(
            STORAGE_ACCOUNT_NAME, 
            storage_key
        )
        blob_service_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        print(f"  ✓ 클라이언트 생성 완료: {blob_service_url}")
        
        # 4. 컨테이너 확인/생성
        print(f"\n[4/5] 컨테이너 확인...")
        container_client = ensure_container_exists(blob_service_client, CONTAINER_NAME)
        
        # 5. 파일 업로드
        print(f"\n[5/5] 파일 업로드...")
        
        # 옵션 1: 단일 파일 업로드
        if os.path.isfile(PDF_FILE_PATH):
            blob_name = upload_single_file(container_client, PDF_FILE_PATH)
            print(f"\n✓ 업로드 성공: {blob_service_url}/{CONTAINER_NAME}/{blob_name}")
        
        # 옵션 2: 폴더 전체 업로드 (DATA_FOLDER가 정의된 경우)
        elif 'DATA_FOLDER' in globals() and os.path.isdir(DATA_FOLDER):
            uploaded_files = upload_folder(container_client, DATA_FOLDER)
            print(f"\n✓ {len(uploaded_files)}개 파일 업로드 완료")
        
        else:
            print(f"⚠️  경로를 찾을 수 없습니다: {PDF_FILE_PATH}")
            return
        
        # 6. 업로드된 파일 목록 확인
        list_blobs(container_client)
        
        print("\n" + "=" * 60)
        print("✅ 모든 작업이 성공적으로 완료되었습니다!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n작업이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n문제 해결 방법:")
        print("  1. Azure 로그인 확인: az account show")
        print("  2. 리소스 그룹 확인: 'pro-kyh-rg'가 존재하는지 확인")
        print("  3. Storage Account 확인: 'prokyhstorage24q19'가 존재하는지 확인")
        print("  4. PDF 파일 경로 확인")
        exit(1)


if __name__ == "__main__":
    main()