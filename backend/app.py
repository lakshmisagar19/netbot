from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS  # Add this import
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from database import db, User, ChatHistory
import requests
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Enable CORS for your frontend Web App (allow only specific frontend URL)
CORS(app, resources={r"/chat": {"origins": "https://netbot-acfpe8htana7bwfw.canadacentral-01.azurewebsites.net"}})  # Replace with your frontend URL

# Configure Google OAuth via Flask-Dance
google_bp = make_google_blueprint(
    client_id=app.config['GOOGLE_OAUTH_CLIENT_ID'],
    client_secret=app.config['GOOGLE_OAUTH_CLIENT_SECRET'],
    scope=["profile", "email"],
    redirect_url="/google_login/authorized"
)
app.register_blueprint(google_bp, url_prefix="/google_login")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home page: login or sign up
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # If the user submits a local login form (for creating a new account or logging in)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')  # In production, hash and verify!
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:  # Replace with secure password check
            login_user(user)
            return redirect(url_for('index'))
        else:
            # Optionally create a new account if not exist (simplest version)
            if not user:
                user = User(email=email, password=password, name=email.split('@')[0])
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('index'))
    return render_template('login.html')

# Route for Google OAuth login
@app.route('/google')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return redirect(url_for('login'))
    
    info = resp.json()
    email = info["email"]
    user = User.query.filter_by(email=email).first()
    if not user:
        # Create a new user
        user = User(email=email, name=info.get("name"))
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('index'))

# Main page (chat interface) after login
@app.route('/index')
@login_required
def index():
    # Fetch previous chats for display
    chats = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).all()
    return render_template('index.html', chats=chats)

# Endpoint to handle chat requests (AJAX call)
@app.route('/chat', methods=['POST'])
@login_required
def chat():
    user_question = request.json.get('question')
    
    # Call Azure OpenAI API
    openai_url = (
        f"{app.config['AZURE_OPENAI_ENDPOINT']}openai/deployments/"
        f"{app.config['AZURE_OPENAI_DEPLOYMENT']}/completions?api-version=2022-12-01"
    )
    headers = {
        "Content-Type": "application/json",
        "api-key": app.config['AZURE_OPENAI_API_KEY']
    }
    payload = {
        "prompt": user_question,
        "max_tokens": 150,
        "temperature": 0.7,
        "model": app.config['AZURE_OPENAI_MODEL']
    }
    
    response = requests.post(openai_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        answer = "Sorry, there was an error processing your request."
    else:
        data = response.json()
        # Adjust according to Azure OpenAI's response format
        answer = data.get("choices", [{}])[0].get("text", "").strip()
    
    # Save the question and answer to the database
    chat_record = ChatHistory(user_id=current_user.id, question=user_question, answer=answer)
    db.session.add(chat_record)
    db.session.commit()
    
    return jsonify({"answer": answer})

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# filepath: /Users/lakshmisagars/network-chatbot/backend/app.py
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, request, jsonify, render_template
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
DATABASE_URL = ("mssql+pyodbc://Admins1:Test!admin123@netbot-sql-server.database.windows.net:1433/netbot-db?driver=ODBC+Driver+18+for+SQL+Server")
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
Base.metadata.create_all(engine)
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

