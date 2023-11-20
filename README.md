# Deploy ML model with flask app

This is a simple Flask app to deploy a trained ML model to API endpoint. The ML model is trained and saved as a pickle file.



# To partly automate the deployment to Azure

- Create Azure Service Principal
- Store appID and secret in Azure key vault
- Store appID and secret locally in config.env file (do not share this in public repository)
- Run deploy.sh file
