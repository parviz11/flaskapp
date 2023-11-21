from flask import Flask, request, jsonify
import pickle
import pandas as pd
from flasgger import Swagger

app = Flask(__name__)
app.config['SWAGGER'] = {'openapi':'3.0.2'}
Swagger(app, template_file='swagger.yml')

# Define a list of valid API keys
with open('app/api_keys.txt') as f:
    valid_api_keys = f.readlines()
f.close()

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

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint for making predictions.

    Returns:
        jsonify: A JSON response containing the prediction result.
    """
    try:
        # Check if the API key is included in the request headers
        api_key = request.headers.get('X-API-Key')

        if api_key not in valid_api_keys:
            return jsonify({"error": "Invalid API key."}), 401  # Unauthorized

        data = request.get_json()

        if data is None:
            return jsonify({"error": "Invalid JSON data received."}), 400

        # Convert the received data into a DataFrame
        input_data = pd.DataFrame(data, index=[0])

        # Make predictions using scikit-learn model
        prediction = model.predict_proba(input_data)

        return jsonify({"prediction": prediction.tolist()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
