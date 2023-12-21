from flask import Flask, request, jsonify
import pickle, os, json, bcrypt
import pandas as pd
from flasgger import Swagger
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from dotenv import load_dotenv
from loguru import logger
from azure.storage.blob import BlobServiceClient

# Load environment variables from .env
'''
This is only useful in development. In production do not use this method.
Instead, store secrets and tokens as environment variables in the 
deployment environment, e.g., Azure App Service.
'''
load_dotenv()

app = Flask(__name__)
app.config['SWAGGER'] = {'openapi':'3.0.2'}
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES'))

jwt = JWTManager(app)
Swagger(app, template_file='swagger.yml')

# Configure Loguru
azure_storage_account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
# Connection string for Azure Storage
connection_string = "DefaultEndpointsProtocol=https;AccountName=flaskappstorage;AccountKey="+azure_storage_account_key+";EndpointSuffix=core.windows.net"

# Container and file names
container_name = "logs"
file_name = "app.log"

# Construct the log file path
log_file_path = f"{connection_string};ContainerName={container_name};BlobName={file_name}"

try:
    # Loguru startup message
    logger.info("Loguru is initializing.")

    # Configure Loguru
    logger.add(log_file_path, rotation="500 MB", compression="zip", level="INFO") # rotate files > 500Mb and write logs min level='INFO'

    # Additional log statement
    logger.info("Loguru setup completed.")

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to a container
    container_client = blob_service_client.get_container_client(container_name)

    # Upload the log file to Azure Blob Storage
    with open("app/app.log", "rb") as data:
        container_client.upload_blob(name=file_name, data=data)
        
except Exception as e:
    # Log any configuration errors
    logger.error(f"Loguru configuration error: {str(e)}")



# Load the trained model
with open("app/model/lg_pipeline_v1_0.pkl", "rb") as model_file:
    model = pickle.load(model_file)
model_file.close()

# Load column types.
'''
It is important to specify column types because when
a client sends request to /predict endpoint
they take a row of a pandas data frame and convert
it to json format. /predict endpoint then takes
this json formatted data and converts it to Python
dictionary. Thereafter, pandas DataFrame method is 
applied to convert the dictionary to data frame. At
this point, the information about column dtypes are
lost and sklearn Pipeline might not work as expected.

Note. Check if it is possible to apply this logic in
the Pipeline. If yes, remove this block and corresponding
part of the code in /predict method below.
'''
with open("app/data/col_dtypes.json", "r") as columns_file:
    column_data_types = json.load(columns_file)
columns_file.close()

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint for health checks.

    A JSON response indicating the health status of the application.
    """
    # Perform health checks here
    # Return a 200 OK response if the app is healthy, otherwise 500
    try:
        # Info log, success
        logger.info("Health check passed successfully")
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"error": "Health check failed"}), 500

# Authentication function
def authenticate_user(username, password):
    """
    Simple authentication method.

    Args:
        username (str): The username.
        password (str): The password.

    Returns:
        bool: True if authentication is successful, False otherwise.
    """
    # Retrieve the hashed version of the password
    stored_password_hash = os.getenv('APP_PASSWORD_HASH').encode('utf-8')

    # Hash entered password and check agains the retrieved hashed value
    if username == os.getenv('APP_USERNAME') and bcrypt.checkpw(password.encode('utf-8'), stored_password_hash):
        return True
    else:
        return False

@app.route('/login', methods=['POST'])
def login():
    """
    Endpoint for user authentication.

    Returns:
        jsonify: A JSON response containing the access token.
    """
    try:
        # Authenticate
        username = request.json.get('username')
        password = request.json.get('password')

        # Check if username-password are correct
        if authenticate_user(username, password):
            # Create JWT token with user identity
            access_token = create_access_token(identity=username)
            # Info log, success
            logger.info(f"User logged in successfully: {username}")

            return jsonify(access_token=access_token), 200
        else:
            logger.warning(f"Invalid login attempt for user: {username}")
            return jsonify({"error": "Invalid credentials."}), 401

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    """
    Endpoint for making predictions.

    Returns:
        jsonify: A JSON response containing the prediction result.
    """
    try:
        # Check if the API key is included in the request headers
        api_key = request.headers.get('Authorization', '').split('Bearer ')[-1]

        # Access the identity of the current user with get_jwt_identity
        current_user = get_jwt_identity()

        data = request.get_json()

        if data is None:
            logger.warning("Invalid JSON data received in /predict")
            return jsonify({"error": "Invalid JSON data received."}), 400

        # Convert the received data into a DataFrame
        input_data = pd.DataFrame(data, index=[0]).astype(column_data_types)

        # Make predictions using scikit-learn model
        prediction = model.predict_proba(input_data)

        logger.info(f"Prediction made for user: {current_user}")
        return jsonify({"prediction": prediction.tolist(), "user": current_user})

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
