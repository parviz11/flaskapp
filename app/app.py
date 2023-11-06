from flask import Flask, request, jsonify
import pickle

app = Flask(__name)

# Define a list of valid API keys
with open('app/api_keys.txt') as f:
    valid_api_keys = f.readlines()
f.close()

# Load the trained model
with open("app/model/lg_pipeline.pkl", "rb") as model_file:
    model = pickle.load(model_file)
model_file.close()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if the API key is included in the request headers
        api_key = request.headers.get('X-API-Key')

        if api_key not in valid_api_keys:
            return jsonify({"error": "Invalid API key."}), 401  # Unauthorized

        data = request.get_json()

        if data is None:
            return jsonify({"error": "Invalid JSON data received."}), 400

        # Perform data preprocessing if necessary
        # Make predictions using your scikit-learn model
        prediction = model.predict_proba(data)

        return jsonify({"prediction": prediction.tolist()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    # Perform health checks here
    # Return a 200 OK response if the app is healthy
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
