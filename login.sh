#!/bin/bash

# Load configuration from file
source config.env

# Set the default subscription
az account set --subscription $AZURE_SUBSCRIPTION_ID

# Log in to Azure
az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID