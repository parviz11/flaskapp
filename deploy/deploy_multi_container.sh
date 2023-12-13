#!/bin/bash

# Source the login script
source deploy/login.sh

# Load configuration from file
source deploy/config.env

start_date_time=$(date)

echo "Successfully logged in."

# Key Vault and Secret Names
keyVaultName="flaskappkeys"
appIdSecretName="appID"
passwordSecretName="password"

# App login and API token
jwtSecretName="jwtsecretkey"
apiloginUserName="apiloginuser"
apiloginPass="apiloginpass"
apiloginpassHash="apiloginpasshash"

# Resource Group and Deployment Variables
resourceGroup="flaskapp"
containerRegistry="flaskappcontainer"
aciContext=flaskacicontext
containerInstance="flaskappaci"
webAppName="flaskappwebapp"
webAppServicePlan="flaskappwebplan"
image="flaskapp"

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


# Continue with deployment using the retrieved secrets
echo "Successfully retrieved Service Principal Secrets."
echo "App ID: $appId"
echo "Password: [hidden]"


# Check if Azure Container Registery resource with this name exists
acrExists=$(az acr show --name $containerRegistry --resource-group $resourceGroup --query "name" --output tsv 2>/dev/null)

if [ -z "$acrExists" ]; then
    # ACR does not exist, create it
    echo "Creating Azure Container Registry..."

    # Create Azure Container Registery resource
    az acr create --resource-group $resourceGroup --name $containerRegistry --sku Basic --admin-enabled true
    if [ $? -ne 0 ]; then
        echo "Failed to create the Azure Container Registry."
        exit 1
    fi

    echo "Azure Container Registry created successfully."
else
    echo "Azure Container Registry '$containerRegistry' already exists. Skipping creation."
fi



# Login with Docker. Login to Azure to be able to push locally built images to ACR.
docker login $containerRegistry.azurecr.io --username $AZURE_CLIENT_ID --password $AZURE_CLIENT_SECRET
docker login azure --resource-group $resourceGroup --username $AZURE_CLIENT_ID --password $AZURE_CLIENT_SECRET

# Build Docker Compose images locally
docker-compose build

echo "Successfully built the Docker images"

# Push Docker Compose images to Azure Container Registry
docker-compose push

echo "Successfully pushed the images."

# Run containers in Azure Container Instance
docker context create aci $aciContext

docker context use $aciContext

docker compose up --detached

echo "Containers are up and running."
# Deploy to web app to azure

## Create App Service plan
az appservice plan create --name $webAppServicePlan --resource-group $resourceGroup --sku B1 --is-linux
if [ $? -ne 0 ]; then
    echo "Failed to create the App Service plan."
    exit 1
fi
# Use $appId and $password in deployment process
# Deploy to web app in Azure Container Registry
az webapp create --resource-group $resourceGroup --plan $webAppServicePlan --name $webAppName \
    --docker-registry-server-password $password --docker-registry-server-user $appId \
    --multicontainer-config-type compose --multicontainer-config-file docker-compose.yml
    
if [ $? -ne 0 ]; then
    echo "Failed to deploy the web app to Azure."
    exit 1
fi

az webapp config appsettings set --resource-group $resourceGroup --name $webAppName \
    --settings JWT_SECRET_KEY=$jwtsecret JWT_ACCESS_TOKEN_EXPIRES=6000 APP_USERNAME=$apiuser APP_PASSWORD_HASH=$apipasshash

echo "Web app deployed successfully."

end_date_time=$(date)
echo "Process started at $start_date_time and finished at $end_date_time"