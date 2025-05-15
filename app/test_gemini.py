import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")
print(API_KEY)
genai.configure(api_key="API_KEY")

try:
    models = genai.list_models()
    for model in models:
        print(f"{model.name} — {model.supported_methods}")
except Exception as e:
    print(f"Error: {e}")