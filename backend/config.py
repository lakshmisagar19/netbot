# config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    
    # Azure SQL Database settings: format the connection string as needed.
    # Example for SQL Server using pyodbc:
    SQLALCHEMY_DATABASE_URI = ("mssql+pyodbc://Admins1:Test!admin123@netbot-sql-server.database.windows.net:1433/netbot-db?driver=ODBC+Driver+18+for+SQL+Server")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Azure OpenAI settings
    AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT') or 'https://laksh-m6o1120w-swedencentral.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview'
    AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY') or  '4OMK9HRD55hC1OGc7CpBPxX3YCfudE7wD47SDOxDdLYEKm3S1PCuJQQJ99BBACfhMk5XJ3w3AAAAACOG0QK9'
    AZURE_OPENAI_DEPLOYMENT = os.environ.get('AZURE_OPENAI_DEPLOYMENT') or 'gpt-4o'
    AZURE_OPENAI_MODEL = os.environ.get('AZURE_OPENAI_MODEL') or 'gpt-4o'

   # Google OAuth settings for Flask-Dance
    OAUTHLIB_INSECURE_TRANSPORT = True  # Remove this in production (HTTPS required)
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID') or '422511857045-gc2s8aff1m1t129dp1cd0k3pibenvl5k.apps.googleusercontent.com'
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET') or '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'






