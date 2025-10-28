@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

rem Set values for your subscription and resource group
set subscription_id=dc6618c1-53d2-4bc8-ab82-68140c3fbde1
set resource_group=pro-kyh-rg
set location=francecentral

rem Get random numbers to create unique resource names
set unique_id=!random!!random!

echo Creating storage...
call az storage account create --name prokyhstorage!unique_id! --subscription !subscription_id! --resource-group !resource_group! --location !location! --sku Standard_LRS --encryption-services blob --default-action Allow --allow-blob-public-access true --only-show-errors --output none

echo Uploading files...
rem Hack to get storage key
for /f "tokens=*" %%a in ( 
'az storage account keys list --subscription !subscription_id! --resource-group !resource_group! --account-name prokyhstorage!unique_id! --query "[?keyName=='key1'].{keyName:keyName, permissions:permissions, value:value}"' 
) do ( 
set key_json=!key_json!%%a 
) 
set key_string=!key_json:[ { "keyName": "key1", "permissions": "Full", "value": "=!
set AZURE_STORAGE_KEY=!key_string:" } ]=!
call az storage container create --account-name prokyhstorage!unique_id! --name margies --public-access blob --auth-mode key --account-key %AZURE_STORAGE_KEY% --output none
call az storage blob upload-batch -d margies -s data --account-name prokyhstorage!unique_id! --auth-mode key --account-key %AZURE_STORAGE_KEY%  --output none

echo Creating search service...
echo (If this gets stuck at '- Running ..' for more than a couple minutes, press CTRL+C then select N)
call az search service create --name prokyhaisrch!unique_id! --subscription !subscription_id! --resource-group !resource_group! --location !location! --sku basic --output none

echo -------------------------------------
echo Storage account: prokyhstorage!unique_id!
call az storage account show-connection-string --subscription !subscription_id! --resource-group !resource_group! --name prokyhstorage!unique_id!
echo ----
echo Search Service: prokyhaisrch
echo  Url: https://prokyhaisrch!unique_id!.search.windows.net
echo  Admin Keys:
call az search admin-key show --subscription !subscription_id! --resource-group !resource_group! --service-name prokyhaisrch!unique_id!
echo  Query Keys:
call az search query-key list --subscription !subscription_id! --resource-group !resource_group! --service-name prokyhaisrch!unique_id!

