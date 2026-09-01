import os
from dotenv import load_dotenv

def load_config(app):
    load_dotenv()
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL", "sqlite:///var/bonzibuddy.db")
    
    # Oura OAuth Configuration
    app.config["OURA_CLIENT_ID"] = os.getenv("OURA_CLIENT_ID")
    app.config["OURA_CLIENT_SECRET"] = os.getenv("OURA_CLIENT_SECRET")
    app.config["OURA_REDIRECT_URI"] = os.getenv("OURA_REDIRECT_URI", "http://127.0.0.1:5000/callback")
    app.config["OURA_SCOPE"] = os.getenv("OURA_SCOPE", "daily email personal")
    
    # Oura API URLs
    app.config["OURA_AUTHORIZE_URL"] = "https://cloud.ouraring.com/oauth/authorize"
    app.config["OURA_TOKEN_URL"] = "https://api.ouraring.com/oauth/token"
    app.config["OURA_API_BASE_URL"] = "https://api.ouraring.com/"
