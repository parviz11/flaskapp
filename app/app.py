from flask import Flask, request, jsonify
import pickle, os, json
import pandas as pd
from flasgger import Swagger
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from dotenv import load_dotenv

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


# Load the trained model
with open("app/model/lg_pipeline.pkl", "rb") as model_file:
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
    # Return a 200 OK response if the app is healthy
    return jsonify({"status": "healthy"})

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
    if username == os.getenv('APP_USERNAME') and password == os.getenv('APP_PASSWORD'):
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
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"error": "Invalid credentials."}), 401

    except Exception as e:
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
            return jsonify({"error": "Invalid JSON data received."}), 400

        # Convert the received data into a DataFrame
        input_data = pd.DataFrame(data, index=[0]).astype(column_data_types)

        # Make predictions using scikit-learn model
        prediction = model.predict_proba(input_data)

        return jsonify({"prediction": prediction.tolist(), "user": current_user})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
