from google import genai
from google.genai import types
import os

def query_genai():
    API_KEY = os.getenv("API_KEY")
    client = genai.Client(
        api_key=API_KEY,
        http_options=types.HttpOptions(api_version='v1alpha')
    )

