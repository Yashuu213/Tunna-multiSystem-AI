import os
import sys

# Change to workspace dir
os.chdir(r"c:\Users\SVI\Downloads\Tunna-multiSystem-AI-main\Tunna-multiSystem-AI-main")

from utils.ai_config import is_ai_ready, generate_content_with_retry, get_env_path
from dotenv import load_dotenv

print(f"Env Path: {get_env_path()}")
load_dotenv(get_env_path())
print("Google API Key in env:", bool(os.getenv("GOOGLE_API_KEY")))
print("Groq API Key in env:", bool(os.getenv("GROQ_API_KEY")))
print("OpenRouter Key in env:", bool(os.getenv("OPENROUTER_API_KEY")))
print("Is AI Ready?:", is_ai_ready())

print("Pinging Gemini...")
result = generate_content_with_retry("Hello")
print("Result:", result)
