import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

dot_env_path = Path(__file__).parents[2] / ".env"
if dot_env_path.is_file():
    load_dotenv(dotenv_path=dot_env_path)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY, vertexai=False)
