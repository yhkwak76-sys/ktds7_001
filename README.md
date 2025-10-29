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


AI를 활용한 기술문서 자동 요약 및 오류 분석
본 문서는 Azure AI Search 서비스를 활용하여 PDF 문서를 효율적으로 검색하고 분석하기 위한 인덱싱 구축하고 주요 내용과 단계를 요약합니다.

1. 프로젝트 개요
이 프로젝트는 ./data 디렉터리에 저장된 PDF 파일들을 Azure Blob Storage에 업로드하고, Azure AI Search를 이용하여 해당 문서들의 내용을 인덱싱하여 검색 가능한 상태로 만드는 것을 목표로 합니다. 특히, Azure OpenAI와의 연동을 통한 고급 분석(기술 세트) 가능성을 염두에 두고 있습니다.

2. 사용된 기술 스택 및 환경
운영 체제: Windows
프로그래밍 언어: Python 3.11.9
클라우드 플랫폼: Microsoft Azure
주요 Azure 서비스:
Azure Storage Account (Blob Storage)
Azure AI Search Service
Azure OpenAI Service (기술 세트 연동 시)
주요 도구: Azure CLI
3. 사전 요구 사항 (Prerequisites)
본 프로젝트를 진행하기 위해서는 다음 환경 및 자격 증명이 필요합니다.

Azure 계정 및 활성 구독: 작업을 위한 Azure 구독 ID: dc6618c1-53d2-4bc8-ab82-68140c3fbde1
Azure CLI 설치 및 로그인:
az login
Python 3.11.9 설치: 관련 라이브러리 설치를 위해 필요합니다.
./data 디렉터리에 PDF 문서 존재: 인덱싱할 실제 PDF 파일들이 준비되어 있어야 합니다.
4. 프로젝트 구성 및 리소스 정보
리소스 그룹: pro-kyh-rg
스토리지 계정 이름: prokyhstorage[랜덤값] (생성 시 할당된 전체 이름 확인 필요)
스토리지 컨테이너: PDF 파일을 저장할 컨테이너 (예: pdf-documents)
Azure Cognitive Search 서비스 이름: (추후 생성 시 이름 지정)
Azure OpenAI 서비스 이름: (추후 생성 시 이름 지정, 기술 세트 연동 시 필요)
5. 주요 작업 단계
이 프로젝트는 다음과 같은 순서로 진행됩니다. 각 단계는 Azure CLI 명령어를 통해 실행될 수 있습니다.

5.1. Azure 스토리지 계정 생성
PDF 파일을 저장할 Azure Blob Storage 계정을 생성합니다. (prokyhstorage%RANDOM%)



### 예시: 스토리지 계정 생성 (Storage account name은 고유해야 함)
az storage account create \
  --name <스토리지-계정-이름> \
  --resource-group pro-kyh-rg \
  --location eastus \
  --sku Standard_LRS # 또는 Standard_GRS 등 필요에 따라 변경
5.2. 스토리지 컨테이너 생성 및 PDF 파일 업로드
생성된 스토리지 계정 내에 PDF 파일을 저장할 Blob 컨테이너를 생성하고, 로컬 ./data 폴더의 PDF 파일들을 업로드합니다.

bash


### 예시: 컨테이너 생성
az storage container create \
  --name pdf-documents \
  --account-name <스토리지-계정-이름> \
  --public-access off

# 예시: 로컬 PDF 파일 업로드 (Blob Storage 컨테이너에)
# (이 부분은 스크립트 또는 반복 명령을 통해 './data' 내 모든 PDF 파일을 업로드하도록 구성)
# 예시: 하나의 파일 업로드
az storage blob upload \
  --container-name pdf-documents \
  --file ./data/sample.pdf \
  --name sample.pdf \
  --account-name <스토리지-계정-이름>
5.3. Azure Cognitive Search 서비스 생성 (선택 사항)
아직 검색 서비스가 없다면 생성해야 합니다.

bash


# 예시: 검색 서비스 생성
az search service create \
  --name <검색-서비스-이름> \
  --resource-group pro-kyh-rg \
  --sku Basic \
  --location eastus
5.4. 데이터 소스(Data Source) 생성
Azure Cognitive Search가 PDF 파일이 저장된 스토리지 컨테이너에 접근할 수 있도록 데이터 소스를 정의합니다.

bash


# 예시: 데이터 소스 생성 (REST API 또는 SDK를 통해)
# 이 부분은 일반적으로 Azure Portal, Postman, 또는 Python SDK를 통해 설정합니다.
# Azure CLI에 직접적인 'az search data-source create' 명령은 아직 없습니다.
# (대략적인 JSON payload 구조)
# {
#   "name": "pdf-datasource",
#   "type": "azureblob",
#   "credentials": {
#     "connectionString": "DefaultEndpointsProtocol=https;AccountName=<스토리지-계정-이름>;AccountKey=<스토리지-계정-키>"
#   },
#   "container": {
#     "name": "pdf-documents"
#   },
#   "dataChangeDetectionPolicy": null,
#   "dataDeletionDetectionPolicy": null
# }
5.5. 기술 세트(Skillset) 생성
PDF 파일 내 텍스트 추출을 넘어, 추가적인 고급 분석(예: 엔터티 인식, 핵심 문구 추출, OCR 등)이 필요할 때 기술 세트를 활용합니다. Azure OpenAI와 연동하여 LLM 기반 분석을 수행할 수도 있습니다.

bash


# 예시: 기술 세트 생성 (REST API 또는 SDK를 통해)
# 이 또한 Azure CLI에 직접적인 명령은 없고, 주로 SDK나 REST API로 정의합니다.
# (대략적인 JSON payload 구조)
# {
#   "name": "pdf-skillset",
#   "description": "Extract text from PDF and perform entity recognition.",
#   "skills": [
#     {
#       "@odata.type": "#Microsoft.Skills.Vision.OcrSkill",
#       "name": "extract-content",
#       "description": "Extracts text from PDF document.",
#       "context": "/document",
#       "textExtractionAlgorithm": null,
#       "inputs": [ ... ],
#       "outputs": [ ... ]
#     },
#     // Azure OpenAI Custom Skill 추가 가능
#   ]
# }
5.6. 인덱스(Index) 생성
검색 가능한 문서의 구조와 필드를 정의합니다. 어떤 정보들을 검색 필드로 사용할지, 데이터 타입은 무엇인지 등을 명시합니다.

bash


# 예시: 인덱스 생성 (REST API 또는 SDK를 통해)
# {
#   "name": "pdf-search-index",
#   "fields": [
#     {"name": "id", "type": "Edm.String", "key": true, "filterable": false, "sortable": false, "facetable": false},
#     {"name": "content", "type": "Edm.String", "searchable": true, "filterable": true, "analyzer": "ko.microsoft"},
#     {"name": "metadata_storage_name", "type": "Edm.String", "searchable": true, "filterable": true, "sortable": true},
#     {"name": "location", "type": "Edm.String", "searchable": false, "filterable": false, "sortable": false},
#     {"name": "language", "type": "Edm.String", "searchable": false, "filterable": true}
#     // 기술 세트에서 추출한 필드 추가
#   ],
#   "suggesters": [],
#   "scoringProfiles": [],
#   "defaultScoringProfile": null,
#   "corsOptions": null
# }
5.7. 인덱서(Indexer) 생성
데이터 소스에서 데이터를 읽어와 인덱스에 매핑하고, 필요하다면 기술 세트를 적용하는 자동화된 프로세스를 정의합니다. 인덱서가 실행되면 PDF 파일의 내용이 인덱스에 채워집니다.

bash


# 예시: 인덱서 생성 (REST API 또는 SDK를 통해)
# {
#   "name": "pdf-indexer",
#   "dataSourceName": "pdf-datasource",
#   "targetIndexName": "pdf-search-index",
#   "skillsetName": "pdf-skillset", # 기술 세트를 사용하는 경우 추가
#   "fieldMappings": [],
#   "outputFieldMappings": [],
#   "schedule": {
#     "interval": "PT2H" # 2시간마다 실행
#   },
#   "parameters": {
#     "configuration": {
#       "dataToExtract": "contentAndMetadata",
#       "parsingMode": "default",
#       "imageAction": "generateNormalizedText"
#     }
#   }
# }
6. 다음 단계
인덱서가 정상적으로 실행되는지 모니터링합니다.
Azure Portal 또는 REST API를 통해 인덱싱된 데이터를 검색하여 결과를 확인합니다.
필요에 따라 인덱스 스키마, 기술 세트 또는 인덱서 설정을 조정하여 검색 품질을 최적화합니다.


