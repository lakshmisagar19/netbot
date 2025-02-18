import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import openai

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

# Configure Google OAuth with Flask-Dance
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="/google_login/callback"
)
app.register_blueprint(google_bp, url_prefix="/google_login")

# Configure OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Configure the Azure SQL Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

Base = declarative_base()

# Define database models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(256), unique=True, nullable=False)
    name = Column(String(256))

class ChatHistory(Base):
    __tablename__ = "chathistory"
    id = Column(Integer, primary_key=True)
    user_email = Column(String(256))
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables if they do not exist
try:
    Base.metadata.create_all(engine)
except Exception as e:
    print(f"Error creating tables: {e}")

DBSession = sessionmaker(bind=engine)
db_session = DBSession()

@app.route("/")
def index():
    # If not logged in, redirect to Google login
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    # Retrieve user info from Google
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return f"Error: {resp.text}", 500
    user_info = resp.json()

    # Save the user in our database if they don’t exist yet
    email = user_info["email"]
    user = db_session.query(User).filter_by(email=email).first()
    if not user:
        user = User(email=email, name=user_info.get("name", ""))
        db_session.add(user)
        db_session.commit()

    # Render the main page (if you choose to serve HTML from Flask)
    return render_template("index.html", user=user_info)

@app.route("/api/chat", methods=["POST"])
def chat():
    # Ensure the user is authenticated
    if not google.authorized:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Call the OpenAI GPT API
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # or the engine you prefer
            prompt=question,
            max_tokens=150,
            temperature=0.5,
        )
        answer = response.choices[0].text.strip()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Save the conversation in the database
    user_info = google.get("/oauth2/v2/userinfo").json()
    chat_entry = ChatHistory(
        user_email=user_info.get("email"),
        question=question,
        answer=answer,
        timestamp=datetime.utcnow()
    )
    db_session.add(chat_entry)
    db_session.commit()

    return jsonify({"answer": answer})

@app.route("/api/history", methods=["GET"])
def history():
    # Return the chat history for the logged-in user
    if not google.authorized:
        return jsonify({"error": "Unauthorized"}), 401

    user_info = google.get("/oauth2/v2/userinfo").json()
    email = user_info.get("email")
    chats = db_session.query(ChatHistory).filter_by(user_email=email).order_by(ChatHistory.timestamp.desc()).all()
    history_list = [{
        "question": chat.question,
        "answer": chat.answer,
        "timestamp": chat.timestamp.isoformat()
    } for chat in chats]

    return jsonify(history_list)

if __name__ == "__main__":
    # For local development only; in production, use a WSGI server like Gunicorn.
    app.run(debug=True)