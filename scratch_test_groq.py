import os
import sys

os.chdir(r"c:\Users\SVI\Downloads\Tunna-multiSystem-AI-main\Tunna-multiSystem-AI-main")

from dotenv import load_dotenv
from utils.ai_config import get_env_path
from utils.free_ai_fallback import ask_groq

load_dotenv(get_env_path())
print("Testing ask_groq...")
try:
    print(ask_groq("Say 'hello world'"))
except Exception as e:
    print("Error:", e)
