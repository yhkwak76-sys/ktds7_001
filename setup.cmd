@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

rem Set values for your subscription and resource group
set subscription_id=dc6618c1-53d2-4bc8-ab82-68140c3fbde1
set resource_group=pro-kyh-rg
set location=francecentral

rem Get random numbers to create unique resource names
set unique_id=!random!!random!

echo =====================================
echo Azure Cognitive Search Setup for Tibero Documentation
echo =====================================
echo.

echo [1/5] Creating storage account...
call az storage account create ^
    --name prokyhstorage!unique_id! ^
    --subscription !subscription_id! ^
    --resource-group !resource_group! ^
    --location !location! ^
    --sku Standard_LRS ^
    --encryption-services blob ^
    --default-action Allow ^
    --allow-blob-public-access true ^
    --only-show-errors ^
    --output none

if !errorlevel! neq 0 (
    echo ERROR: Failed to create storage account
    exit /b 1
)
echo    Storage account created successfully

echo.
echo [2/5] Getting storage account key...
rem Get storage key
for /f "tokens=*" %%a in ( 
'az storage account keys list --subscription !subscription_id! --resource-group !resource_group! --account-name prokyhstorage!unique_id! --query "[?keyName=='key1'].{keyName:keyName, permissions:permissions, value:value}"' 
) do ( 
set key_json=!key_json!%%a 
) 
set key_string=!key_json:[ { "keyName": "key1", "permissions": "Full", "value": "=!
set AZURE_STORAGE_KEY=!key_string:" } ]=!
echo    Storage key retrieved

echo.
echo [3/5] Creating container and uploading files...
call az storage container create ^
    --account-name prokyhstorage!unique_id! ^
    --name dataset ^
    --public-access blob ^
    --auth-mode key ^
    --account-key %AZURE_STORAGE_KEY% ^
    --output none

if !errorlevel! neq 0 (
    echo ERROR: Failed to create container
    exit /b 1
)
echo    Container 'dataset' created

call az storage blob upload-batch ^
    -d dataset ^
    -s data ^
    --account-name prokyhstorage!unique_id! ^
    --auth-mode key ^
    --account-key %AZURE_STORAGE_KEY% ^
    --output none

if !errorlevel! neq 0 (
    echo WARNING: File upload may have failed
) else (
    echo    Files uploaded successfully
)

echo.
echo [4/5] Creating Azure Cognitive Search service...
echo    (If this gets stuck at '- Running ..' for more than 2 minutes, press CTRL+C then select N)
call az search service create ^
    --name prokyhaisrch!unique_id! ^
    --subscription !subscription_id! ^
    --resource-group !resource_group! ^
    --location !location! ^
    --sku basic ^
    --output none

if !errorlevel! neq 0 (
    echo ERROR: Failed to create search service
    exit /b 1
)
echo    Search service created successfully

echo.
echo [5/5] Creating search index 'tibero-vector'...
rem Get search service admin key
for /f "tokens=*" %%a in (
'az search admin-key show --subscription !subscription_id! --resource-group !resource_group! --service-name prokyhaisrch!unique_id! --query "primaryKey" -o tsv'
) do (
set search_admin_key=%%a
)

if "!search_admin_key!"=="" (
    echo ERROR: Failed to retrieve search admin key
    exit /b 1
)

rem Create index with fields optimized for Tibero documentation (3 documents)
curl -X PUT "https://prokyhaisrch!unique_id!.search.windows.net/indexes/tibero-vector?api-version=2023-11-01" ^
-H "Content-Type: application/json" ^
-H "api-key: !search_admin_key!" ^
-d "{\"name\":\"tibero-vector\",\"fields\":[{\"name\":\"id\",\"type\":\"Edm.String\",\"key\":true,\"searchable\":false},{\"name\":\"content\",\"type\":\"Edm.String\",\"searchable\":true,\"analyzer\":\"ko.lucene\"},{\"name\":\"document_type\",\"type\":\"Edm.String\",\"filterable\":true,\"facetable\":true,\"sortable\":true},{\"name\":\"title\",\"type\":\"Edm.String\",\"searchable\":true},{\"name\":\"error_code\",\"type\":\"Edm.String\",\"searchable\":true,\"filterable\":true,\"sortable\":true},{\"name\":\"term_korean\",\"type\":\"Edm.String\",\"searchable\":true,\"filterable\":true},{\"name\":\"term_english\",\"type\":\"Edm.String\",\"searchable\":true,\"filterable\":true},{\"name\":\"security_category\",\"type\":\"Edm.String\",\"filterable\":true,\"facetable\":true},{\"name\":\"chapter\",\"type\":\"Edm.String\",\"filterable\":true,\"sortable\":true},{\"name\":\"page_number\",\"type\":\"Edm.Int32\",\"filterable\":true,\"sortable\":true},{\"name\":\"metadata\",\"type\":\"Edm.String\",\"searchable\":true,\"filterable\":true},{\"name\":\"file_name\",\"type\":\"Edm.String\",\"filterable\":true,\"sortable\":true},{\"name\":\"timestamp\",\"type\":\"Edm.DateTimeOffset\",\"filterable\":true,\"sortable\":true}],\"suggesters\":[{\"name\":\"sg\",\"searchMode\":\"analyzingInfixMatching\",\"sourceFields\":[\"error_code\",\"term_korean\",\"term_english\",\"content\",\"title\"]}],\"corsOptions\":{\"allowedOrigins\":[\"*\"]}}"

if !errorlevel! neq 0 (
    echo ERROR: Failed to create search index
    exit /b 1
)
echo    Index 'tibero-vector' created successfully

echo.
echo =====================================
echo Deployment Complete!
echo =====================================
echo.
echo STORAGE ACCOUNT: prokyhstorage!unique_id!
echo Container: dataset
echo.
call az storage account show-connection-string --subscription !subscription_id! --resource-group !resource_group! --name prokyhstorage!unique_id!
echo.
echo -------------------------------------
echo SEARCH SERVICE: prokyhaisrch!unique_id!
echo Url: https://prokyhaisrch!unique_id!.search.windows.net
echo Index: tibero-vector
echo.
echo Admin Keys:
call az search admin-key show --subscription !subscription_id! --resource-group !resource_group! --service-name prokyhaisrch!unique_id!
echo.
echo Query Keys:
call az search query-key list --subscription !subscription_id! --resource-group !resource_group! --service-name prokyhaisrch!unique_id!
echo.
echo =====================================
echo Next Steps:
echo 1. Create a data source pointing to the 'dataset' container
echo 2. Create a skillset for PDF processing and text extraction
echo 3. Create an indexer to populate the 'tibero-vector' index
echo =====================================

ENDLOCAL