import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Only runs once even if imported multiple times
api_key = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI()
