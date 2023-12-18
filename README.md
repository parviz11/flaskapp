# Deploy ML model with flask app

This is a simple Flask app that demonstrates how to deploy a trained ML model to API endpoint. The ML model is trained and saved as a pickle file. Showing how we trained the model is out of the scope of this exercise.

# File tree


* [.ipynb_checkpoints/](./flaskapp/.ipynb_checkpoints)
  * [API_request-checkpoint.ipynb](./flaskapp/.ipynb_checkpoints/API_request-checkpoint.ipynb)
  * [app_test-checkpoint.ipynb](./flaskapp/.ipynb_checkpoints/app_test-checkpoint.ipynb)
* [app/](./flaskapp/app)
  * [data/](./flaskapp/app/data)
    * [dataset.csv](./flaskapp/app/data/dataset.csv)
  * [model/](./flaskapp/app/model)
    * [lg_pipeline.pkl](./flaskapp/app/model/lg_pipeline.pkl)
  * [.env](./flaskapp/app/.env)
  * [app.py](./flaskapp/app/app.py)
  * [gunicorn.conf.py](./flaskapp/app/gunicorn.conf.py)
  * [swagger.yml](./flaskapp/app/swagger.yml)
* [deploy/](./flaskapp/deploy)
  * [azure_setup_serviceprincipal.txt](./flaskapp/deploy/azure_setup_serviceprincipal.txt)
  * [config.env](./flaskapp/deploy/config.env)
  * [config_file_format.md](./flaskapp/deploy/config_file_format.md)
  * [deploy.sh](./flaskapp/deploy/deploy.sh)
  * [login.sh](./flaskapp/deploy/login.sh)
* [.dockerignore](./flaskapp/.dockerignore)
* [.gitignore](./flaskapp/.gitignore)
* [API_request.ipynb](./flaskapp/API_request.ipynb)
* [Dockerfile](./flaskapp/Dockerfile)
* [README.md](./flaskapp/README.md)
* [app_test.ipynb](./flaskapp/app_test.ipynb)
* [requirements.txt](./flaskapp/requirements.txt)
* [startup.sh](./flaskapp/startup.sh)


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
> **_NOTE:_** Do not include `.env` file in the public repository such as GitHub. Add `.env` in `.gitignore` file to make sure that it will not be accidentally pushed to a public repository.

# Run model locally with Docker

`docker-compose -f docker-compose.yml up`

# Set up

To begin, go to Azure portal and create a resource group. Then create [Service Principal](https://learn.microsoft.com/en-us/cli/azure/azure-cli-sp-tutorial-1?tabs=bash) and Azure Key Vault. Next, assign Key Vault Secrets Officer role using Azure RBAC and login with service principal credentials. Store your secrets in Azure Key Vault. You will need to log in with your Service Principal and retrieve the secrets to further use them in your app's environment configuration. This is one of secure ways of working with secrets (e.g., username, password, token etc.). 

 [!IMPORTANT] For CLI commands, refer to [./deploy/azure_setup_serviceprincipal.txt](https://github.com/parviz11/flaskapp/blob/main/deploy/azure_setup_serviceprincipal.txt) file.

Create `config.env` file and store these parameters in it:

AZURE_SUBSCRIPTION_ID=<value>
AZURE_TENANT_ID=<value>
AZURE_CLIENT_ID=<value>
AZURE_CLIENT_SECRET=<value>

You can obtain these values when you create Service Principal.
Do not store `config.env` file in a public repository. 
Once you have completed setting up resources and configurations you are ready to deploy the app.

# Deploy single container app on Azure



# Deploy a multi-container group using Docker Compose

# To partly automate the deployment to Azure

- Create Azure Service Principal
- Store appID and secret in Azure key vault
- Store appID and secret locally in config.env file (do not share this in public repository)
- Run deploy.sh file
