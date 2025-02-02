from flask import Flask, render_template, request, jsonify
import openai
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# Configure Azure OpenAI 
openai.api_type = "azure"
openai.api_base = "https://laksh-m6o1120w-swedencentral.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
openai.api_version = "2024-12-03"
openai.api_key = "4OMK9HRD55hC1OGc7CpBPxX3YCfudE7wD47SDOxDdLYEKm3S1PCuJQQJ99BBACfhMk5XJ3w3AAAAACOG0QK9"  # Replace with your Azure OpenAI API key #

# Configure Azure SQL Database 
DATABASE_URI = "mssql+pyodbc://Admins1:Testadmin@123@netbot-sql-server.database.windows.net:1433/netbot-db?driver=ODBC+Driver+18+for+SQL+Server"
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    questions = Column(Text)

# Create the database tables
Base.metadata.create_all(engine)

@app.route('/')
def home():
    return render_template('index.html')  # Serve the frontend

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data['question']

    # Call Azure OpenAI API
    response = openai.Completion.create(
        engine="YOUR_ENGINE_NAME",  # Replace with your Azure OpenAI engine name
        prompt=question,
        max_tokens=150
    )

    answer = response.choices[0].text.strip()
    links = ["https://example.com/link1", "https://example.com/link2"]  # Replace with actual links based on the question

    # Save question and answer to database
    session = Session()
    user = session.query(User).filter_by(email="user@example.com").first()  # Replace with actual user email
    if user:
        user.questions += f"\nQ: {question}\nA: {answer}"
    else:
        user = User(email="user@example.com", questions=f"Q: {question}\nA: {answer}")
        session.add(user)
    session.commit()
    session.close()

    return jsonify({
        'answer': answer,
        'links': links
    })

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask server