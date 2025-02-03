# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
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
