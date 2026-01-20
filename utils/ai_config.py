
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
AI_AVAILABLE = False

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        AI_AVAILABLE = True
    except ImportError:
        print("WARNING: google-generativeai library not found.")
        AI_AVAILABLE = False

# Priority list of models to try
MODEL_POOL = [
    'gemini-3-flash-preview',
    'gemini-2.0-flash-exp',
    'gemini-2.5-flash', 
    'gemini-2.0-flash'
]

def generate_content_with_retry(content_payload):
    """Helper to call Gemini with robust error handling."""
    if not AI_AVAILABLE:
        raise Exception("AI Library not available.")

    # Try models in priority order
    for model_name in MODEL_POOL:
        try:
            # Rate limit protection: Wait 0.5s between model switches
            time.sleep(0.5) 
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(content_payload)
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                print(f"⚠️ Limit Hit on {model_name}. Trying next...")
                time.sleep(1) 
            elif "404" in error_str:
                print(f"⚠️ Model {model_name} not found. Trying next...")
            else:
                print(f"Model {model_name} error: {error_str}")

    # If all failed
    raise Exception("QUOTA_EXCEEDED or ALL MODELS FAILED")
