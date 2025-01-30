from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Now you can access your API keys securely
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2023-05-15")
print(AZURE_OPENAI_API_KEY)




