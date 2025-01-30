from flask import Flask, render_template, request, jsonify
import openai
import os
from flask_cors import CORS


# Initialize the Flask app
app = Flask(__name__)
CORS(app, origins=["https://chatbot-frontend.azurewebsites.net"])


# Load your OpenAI API key from the environment or config file
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')  # Render the main page (index.html)

@app.route('/ask', methods=['POST'])
def ask():
    # Get the question from the JSON payload
    data = request.get_json()  # Use request.get_json() to retrieve JSON data
    user_question = data.get('question')

    if not user_question:
        return jsonify({"error": "No question provided"}), 400  # Return an error if the question is missing

    # Send the question to the OpenAI API (GPT)
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Or whichever model you prefer
            prompt=user_question,
            max_tokens=150
        )
        
        # Return the answer from GPT as a JSON response
        return jsonify({"answer": response.choices[0].text.strip()})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return an error if something goes wrong with the API request

if __name__ == '__main__':
    app.run(debug=True)

