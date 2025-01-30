from flask import Flask, request, jsonify, make_response
import openai
import os
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)

# Configure CORS to allow requests from your frontend
CORS(app, resources={r"/ask": {"origins": "https://netbot-acfpe8htana7bwfw.canadacentral-01.azurewebsites.net"}}, supports_credentials=True)

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Handle Preflight Requests (OPTIONS)
@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "https://netbot-acfpe8htana7bwfw.canadacentral-01.azurewebsites.net")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

@app.route('/')
def home():
    return jsonify({"message": "Flask server is running!"})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_question = data.get('question')

    if not user_question:
        return jsonify({"error": "No question provided"}), 400  

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  
            prompt=user_question,
            max_tokens=150
        )
        return jsonify({"answer": response.choices[0].text.strip()})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Use 0.0.0.0 for Azure compatibility
