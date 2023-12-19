# Deploy ML model with flask app

This is a simple Flask app that demonstrates how to deploy a trained ML model to API endpoint. The ML model is trained and saved as a pickle file. Showing how we trained the model is out of the scope of this exercise.

# File tree

- [app/](https://github.com/parviz11/flaskapp/tree/main/app)
  - [data/](https://github.com/parviz11/flaskapp/tree/main/app/data)
    - [col_dtypes.json](https://github.com/parviz11/flaskapp/blob/main/app/data/col_dtypes.json)
    - [dataset.csv](https://github.com/parviz11/flaskapp/blob/main/app/data/dataset.csv)
  - [model/](https://github.com/parviz11/flaskapp/tree/main/app/model)
    - [lg_pipeline_v1_0.pkl](https://github.com/parviz11/flaskapp/blob/main/app/model/lg_pipeline_v1_0.pkl)
    - [lg_pipeline_v1_1.pkl](https://github.com/parviz11/flaskapp/blob/main/app/model/lg_pipeline_v1_1.pkl)
  - [app.py](https://github.com/parviz11/flaskapp/blob/main/app/app.py)
  - [gunicorn.conf.py](https://github.com/parviz11/flaskapp/blob/main/app/gunicorn.conf.py)
  - [swagger.yml](https://github.com/parviz11/flaskapp/blob/main/app/swagger.yml)

- [deploy/](https://github.com/parviz11/flaskapp/tree/main/deploy)
  - [azure_setup_serviceprincipal.txt](https://github.com/parviz11/flaskapp/blob/main/deploy/azure_setup_serviceprincipal.txt)
  - [config_file_format.md](https://github.com/parviz11/flaskapp/blob/main/deploy/config_file_format.md)
  - [deploy.sh](https://github.com/parviz11/flaskapp/blob/main/deploy/deploy.sh)
  - [deploy_multi_container_app.sh](https://github.com/parviz11/flaskapp/blob/main/deploy/deploy_multi_container_app.sh)
  - [login.sh](https://github.com/parviz11/flaskapp/blob/main/deploy/login.sh)

- [nginx/](https://github.com/parviz11/flaskapp/tree/main/nginx)
  - [Dockerfile](https://github.com/parviz11/flaskapp/blob/main/nginx/Dockerfile)
  - [scoringapp.conf](https://github.com/parviz11/flaskapp/blob/main/nginx/scoringapp.conf)

- [tests/](https://github.com/parviz11/flaskapp/tree/main/tests)
  - [Azure/](https://github.com/parviz11/flaskapp/tree/main/tests/Azure)
    - [Metrics.png](https://github.com/parviz11/flaskapp/blob/main/tests/Azure/Metrics.png)
  - [local_deployment/](https://github.com/parviz11/flaskapp/tree/main/tests/local_deployment)
    - [Docker.png](https://github.com/parviz11/flaskapp/blob/main/tests/local_deployment/Docker.png)
    - [Postman.png](https://github.com/parviz11/flaskapp/blob/main/tests/local_deployment/Postman.png)

- [.dockerignore](https://github.com/parviz11/flaskapp/blob/main/.dockerignore)
- [.gitignore](https://github.com/parviz11/flaskapp/blob/main/.gitignore)
- [Dockerfile](https://github.com/parviz11/flaskapp/blob/main/Dockerfile)
- [README.md](https://github.com/parviz11/flaskapp/blob/main/README.md)
- [docker-compose-azure.yml](https://github.com/parviz11/flaskapp/blob/main/docker-compose-azure.yml)
- [docker-compose.yml](https://github.com/parviz11/flaskapp/blob/main/docker-compose.yml)
- [requirements.txt](https://github.com/parviz11/flaskapp/blob/main/requirements.txt)



# app directory
This directory includes data, the model (trained with `scikit-learn` and saved as the pipeline as a pickle file), and `app.py` file that defines the `flask` application. `swagger.yml` defines the outline of Swagger UI which can be reached after the model deployment through this link: <http://your_app_main_url/apidocs>. `gunicorn.conf.py` file defines the settings for `guinicorn`.

# `app.py `: Environment variables
You can store environment variables in `.env` file at dev/test time. These variables are loaded with `dotenv` library as follows:

```
from dotenv import load_dotenv
load_dotenv()
```

`.env` file content can look like this:

```
# .env
JWT_SECRET_KEY=some_random_token #Random token
JWT_ACCESS_TOKEN_EXPIRES=600  # Set your desired expiration time in seconds
```
> [!NOTE] 
> Do not include `.env` file in the public repository such as GitHub. Add `.env` in `.gitignore` file to make sure that it will not be accidentally pushed to a public repository.

# Run model locally with Docker

`docker-compose -f docker-compose.yml up`

# Set up

To begin, go to Azure portal and create a resource group. Then create [Service Principal](https://learn.microsoft.com/en-us/cli/azure/azure-cli-sp-tutorial-1?tabs=bash) and Azure Key Vault. Next, assign Key Vault Secrets Officer role using Azure RBAC and login with service principal credentials. Store your secrets in Azure Key Vault. You will need to log in with your Service Principal and retrieve the secrets to further use them in your app's environment configuration. This is one of secure ways of working with secrets (e.g., username, password, token etc.). 

> [!IMPORTANT]  
> For CLI commands, refer to [./deploy/azure_setup_serviceprincipal.txt](https://github.com/parviz11/flaskapp/blob/main/deploy/azure_setup_serviceprincipal.txt)

Create `config.env` file and store these parameters in it:

```
AZURE_SUBSCRIPTION_ID=<value>
AZURE_TENANT_ID=<value>
AZURE_CLIENT_ID=<value>
AZURE_CLIENT_SECRET=<value>
```

You can obtain these values when you create Service Principal.
Do not store `config.env` file in a public repository. 
Once you have completed setting up resources and configurations you are ready to deploy the app.

# Deploy single container app on Azure

Use [./deploy/deploy.sh](https://github.com/parviz11/flaskapp/blob/main/deploy/deploy.sh) script to deploy on Azure. In bash, run the script by typing: `bash ./deploy/deploy.sh`. <br>
The script does the followings:

* Logs in to your Azure account by using `./deploy/login.sh` script
* Retrieves secrets from Azure Key Vault
* Creates Azure Container Registry (ACR) resource
* Builds a container image in ACR by using Dockerfile in the root directory
* Creates App Service Plan
* Creates App Service, pulls the image from ACR and runs in the App Service
* Adds secrets as environment variables in App Service.

Note that it might take some time to finish the deployment after running the script. You can monitor the deployment process by navigating to Azure App Service > Deployment center > Logs.

# Deploy a multi-container group using Docker Compose

Use [./deploy/deploy_multi_container_app.sh](https://github.com/parviz11/flaskapp/blob/main/deploy/deploy_multi_container_app.sh) script to deploy on Azure. The script does the followings:

* Logs in to your Azure account by using `./deploy/login.sh` script
* Retrieves secrets from Azure Key Vault
* Creates Azure Container Registry (ACR) resource
* Container images:
  * For Flask app, builds a container image in ACR by using Dockerfile in the root directory
  * For `nginx`, builds a container image in ACR by using Dockerfile in `./nginx/Dockerfile`
* Creates App Service Plan
* Creates App Service, instructs the App Service to build multicontainer app by using `docker-compose-azure.yml` file. This pulls the images from ACR and runs them in the App Service.
* Adds secrets as environment variables in App Service.


# Logging
