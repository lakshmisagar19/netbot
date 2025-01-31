from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)

# Configure CORS for your frontend
CORS(app, resources={r"/ask": {"origins": "https://netbot-acfpe8htana7bwfw.canadacentral-01.azurewebsites.net"}}, supports_credentials=True)

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def home():
    return jsonify({"message": "Flask server is running!"})

@app.route('/ask', methods=['POST', 'OPTIONS'])
def ask():
    # Handle CORS Preflight Request
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS Preflight Handled"})
        response.headers.add("Access-Control-Allow-Origin", "https://netbot-acfpe8htana7bwfw.canadacentral-01.azurewebsites.net")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

    # Get user input
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "No question provided"}), 400  

    user_question = data["question"]

    try:
        # Call OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",  
            prompt=user_question,
            max_tokens=150
        )
        answer = response.choices[0].text.strip()

        # Add CORS headers to response
        response_data = jsonify({"answer": answer})
        response_data.headers.add("Access-Control-Allow-Origin", "https://netbot-acfpe8htana7bwfw.canadacentral-01.azurewebsites.net")
        response_data.headers.add("Access-Control-Allow-Credentials", "true")

        return response_data
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  

# Azure App Service uses Gunicorn, so NO app.run() is needed.
