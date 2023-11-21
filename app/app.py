from flask import Flask, request, jsonify
import pickle
import pandas as pd
from flasgger import Swagger
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from dotenv import load_dotenv
import os

# Load environment variables from .env
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

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint for health checks.

    A JSON response indicating the health status of the application.
    """
    # Perform health checks here
    # Return a 200 OK response if the app is healthy
    return jsonify({"status": "healthy"})

# Example route requiring JWT authentication
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Move authentication logic to a separate function or class method
def authenticate_user(username, password):
    # Replace this with your actual authentication logic
    if username == 'admin' and password == 'admin':
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
        # Add your authentication logic here (e.g., check credentials)
        username = request.json.get('username')
        password = request.json.get('password')

        # Replace this with your actual authentication logic
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
        # Access the identity of the current user with get_jwt_identity
        current_user = get_jwt_identity()

        data = request.get_json()

        if data is None:
            return jsonify({"error": "Invalid JSON data received."}), 400

        # Convert the received data into a DataFrame
        input_data = pd.DataFrame(data, index=[0])

        # Make predictions using scikit-learn model
        prediction = model.predict_proba(input_data)

        return jsonify({"prediction": prediction.tolist(), "user": current_user})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
