import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

models = [
    'gemini-3-flash-preview',
    'gemini-2.5-flash',
    'gemini-2.0-flash-exp',
    'gemini-2.0-flash',
    'gemini-1.5-flash' # Trying this again just in case
]

print(f"{'MODEL':<25} | {'STATUS':<20}")
print("-" * 50)

for m in models:
    try:
        model = genai.GenerativeModel(m)
        model.generate_content("test")
        print(f"{m:<25} | {'OK':<20}")
    except Exception as e:
        err = str(e)
        status = "ERROR"
        if "429" in err: status = "429 (QUOTA EXCEEDED)"
        elif "404" in err: status = "404 (NOT FOUND)"
        print(f"{m:<25} | {status:<20}")
