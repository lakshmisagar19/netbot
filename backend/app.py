from flask import Flask, request, jsonify
from flask_cors import CORS
from openai_api import get_chatbot_response

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    response = get_chatbot_response(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)

