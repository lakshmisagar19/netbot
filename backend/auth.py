from flask import Blueprint, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import requests

auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    return User(user_id, session.get("name"), session.get("email"))

@auth_bp.route("/login")
def login():
    google_auth_url = "https://accounts.google.com/o/oauth2/auth"
    return redirect(google_auth_url)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

