from flask import Flask, render_template, request, jsonify
import openai
import os
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS for API requests

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Route to serve the frontend UI
@app.route('/')
def index():
    return render_template('index.html')  # Ensure index.html is inside the 'templates' folder

# API Endpoint for chatbot responses
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

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
