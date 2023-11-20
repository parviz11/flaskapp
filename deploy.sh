#!/bin/bash

# Source the login script
source login.sh

echo "Successfully logged in."

# Key Vault and Secret Names
keyVaultName="flaskappkeys"
appIdSecretName="appID"
passwordSecretName="password"

# Resource Group and Deployment Variables
resourceGroup="flaskapp"
containerRegistry="flaskapp123"
webAppName="flaskapp123"

# Retrieve Service Principal Secrets from Key Vault
echo "Retrieving Service Principal Secrets from Azure Key Vault..."

# Retrieve App ID from Key Vault
appId=$(az keyvault secret show --vault-name $keyVaultName --name $appIdSecretName --query "value" --output tsv)
if [ -z "$appId" ]; then
    echo "Failed to retrieve App ID from Key Vault."
    exit 1
fi

# Retrieve Password from Key Vault
password=$(az keyvault secret show --vault-name $keyVaultName --name $passwordSecretName --query "value" --output tsv)
if [ -z "$password" ]; then
    echo "Failed to retrieve Password from Key Vault."
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

# Build the image in Azure Container Registry
az acr build --resource-group $resourceGroup --registry $containerRegistry --image flaskapp:latest .
if [ $? -ne 0 ]; then
    echo "Failed to build the image in Azure Container Registry."
    exit 1
fi

# Deploy to web app to azure

## Create App Service plan
az appservice plan create --name webplan --resource-group $resourceGroup --sku B1 --is-linux
if [ $? -ne 0 ]; then
    echo "Failed to create the App Service plan."
    exit 1
fi
# Use $appId and $password in your deployment process
# Deploy to web app in Azure Container Registry
az webapp create --resource-group $resourceGroup --plan webplan --name $webAppName \
    --docker-registry-server-password $password --docker-registry-server-user $appId \
    --role acrpull --deployment-container-image-name $containerRegistry.azurecr.io/flaskapp:latest
if [ $? -ne 0 ]; then
    echo "Failed to deploy the web app to Azure."
    exit 1
fi

echo "Web app deployed successfully."