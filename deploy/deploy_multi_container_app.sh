#!/bin/bash

# Source the login script
source deploy/login.sh

start_date_time=$(date)

echo "Successfully logged in."

# Key Vault and Secret Names
keyVaultName="flaskappkeys"
appIdSecretName="appID"
passwordSecretName="password"

# App login and API token
jwtSecretName="jwtsecretkey"
apiloginUserName="apiloginuser"
apiloginpassHash="apiloginpasshash"

# Resource Group and Deployment Variables
resourceGroup="flaskapp"
containerRegistry="flaskappcontainer"
webAppName="flaskappwebapp"
webAppServicePlan="flaskappwebplan"
flaskimage="flaskapp"
nginximage="nginx"

# Retrieve Service Principal Secrets from Key Vault
echo "Retrieving Service Principal Secrets from Azure Key Vault..."

# Retrieve App ID from Key Vault
appId=$(az keyvault secret show --vault-name $keyVaultName --name $appIdSecretName --query "value" --output tsv)
if [ -z "$appId" ]; then
    echo "Failed to retrieve App ID from Key Vault."
    exit 1
fi
echo "Retrieved appID"
# Retrieve Password from Key Vault
password=$(az keyvault secret show --vault-name $keyVaultName --name $passwordSecretName --query "value" --output tsv)
if [ -z "$password" ]; then
    echo "Failed to retrieve Password from Key Vault."
    exit 1
fi
echo "Retrieved pass"
# Retrieve API token initial value
jwtsecret=$(az keyvault secret show --vault-name $keyVaultName --name $jwtSecretName --query "value" --output tsv)
if [ -z "$jwtsecret" ]; then
    echo "Failed to retrieve JWT Secret Key from Key Vault."
    exit 1
fi

# Retrieve API username
apiuser=$(az keyvault secret show --vault-name $keyVaultName --name $apiloginUserName --query "value" --output tsv)
if [ -z "$apiuser" ]; then
    echo "Failed to retrieve API user name from Key Vault."
    exit 1
fi


# Retrieve API pass hash

apipasshash=$(az keyvault secret show --vault-name $keyVaultName --name $apiloginpassHash --query "value" --output tsv)
if [ -z "$apipasshash" ]; then
    echo "Failed to retrieve API password from Key Vault."
    exit 1
fi


# Continue with your deployment using the retrieved secrets
echo "Successfully retrieved Service Principal Secrets."
echo "App ID: $appId"
echo "Password: [hidden]"

# Create Azure Container Registery resource
az acr create --resource-group $resourceGroup --name $containerRegistry --sku Basic --admin-enabled true
if [ $? -ne 0 ]; then
    echo "Failed to create the Azure Container Registry."
    exit 1
fi

# Build flask image in Azure Container Registry
az acr build --resource-group $resourceGroup --registry $containerRegistry --image $flaskimage:latest .
if [ $? -ne 0 ]; then
    echo "Failed to build the image in Azure Container Registry."
    exit 1
fi

echo "$flaskimage image built in ACR"

# Build nginx image in Azure Container Registry
az acr build --resource-group $resourceGroup --registry $containerRegistry --image $nginximage:latest . -f nginx/Dockerfile
if [ $? -ne 0 ]; then
    echo "Failed to build the image in Azure Container Registry."
    exit 1
fi

echo "$nginximage image built in ACR"

# Deploy to web app to azure

## Create App Service plan
az appservice plan create --name $webAppServicePlan --resource-group $resourceGroup --sku B1 --is-linux
if [ $? -ne 0 ]; then
    echo "Failed to create the App Service plan."
    exit 1
fi
# Use $appId and $password in your deployment process
# Deploy to web app in Azure Container Registry
az webapp create --resource-group $resourceGroup --plan $webAppServicePlan --name $webAppName \
    --docker-registry-server-password $password --docker-registry-server-user $appId \
    --multicontainer-config-type compose --multicontainer-config-file docker-compose-azure.yml
    
if [ $? -ne 0 ]; then
    echo "Failed to deploy the web app to Azure."
    exit 1
fi

az webapp config appsettings set --resource-group $resourceGroup --name $webAppName \
    --settings JWT_SECRET_KEY=$jwtsecret JWT_ACCESS_TOKEN_EXPIRES=6000 APP_USERNAME=$apiuser APP_PASSWORD_HASH=$apipasshash

echo "Web app deployed successfully."

end_date_time=$(date)
echo "Process started at $start_date_time and finished at $end_date_time"