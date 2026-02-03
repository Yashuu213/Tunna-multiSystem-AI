
import os
import time
import base64
import io
from dotenv import load_dotenv
from google import genai
from google.genai import types

import sys

load_dotenv()

# --- ROBUST ENV PATH (Fixes Frozen App Logic) ---
def get_env_path():
    """Calculates absolute path to .env file."""
    if getattr(sys, 'frozen', False):
        # In EXE: .env is next to the executable
        base_path = os.path.dirname(sys.executable)
    else:
        # In Dev: .env is in project root (parent of utils/)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, ".env")

# Reload with explicit path
load_dotenv(get_env_path())

def reload_keys():
    """Refreshes API keys from environment (Called after Auth UI)."""
    global API_KEYS, AI_AVAILABLE
    path = get_env_path()
    
    # 1. Load from file (but DO NOT overwrite existing memory keys)
    if os.path.exists(path):
        load_dotenv(path, override=False) 
    
    # 2. Critical: Ensure we strip whitespace if loaded from file
    if os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY").strip()

    # 3. Reload list
    API_KEYS = get_all_api_keys()
    AI_AVAILABLE = len(API_KEYS) > 0
    
    # Debug Log
    print(f"🔄 AI System Reloaded. Path: {path}")
    print(f"🔑 Key Status: Memory={'Yes' if os.getenv('GOOGLE_API_KEY') else 'No'} | Total Keys: {len(API_KEYS)}")

def is_ai_ready():
    """Dynamic check for AI availability."""
    return len(get_all_api_keys()) > 0

def get_all_api_keys():
    keys = []
    if os.getenv("GOOGLE_API_KEY"): keys.append(os.getenv("GOOGLE_API_KEY"))
    for i in range(2, 10): 
        key = os.getenv(f"GOOGLE_API_KEY_{i}")
        if key: keys.append(key)
    return keys

API_KEYS = get_all_api_keys()
AI_AVAILABLE = len(API_KEYS) > 0

MODEL_POOL = [
    'gemini-2.0-flash-thinking-exp-01-21', # Thinking Model (Separate Quota)
    'gemini-2.0-pro-exp-02-05', # BRAND NEW (High Limits)
    'gemini-exp-1206', # Experimental (Region Bypass)
    'gemini-2.0-flash', 
    'gemini-2.0-flash-lite-preview-02-05', # Ultra-new
    'gemini-1.5-flash',
    'gemini-1.5-flash-8b', # High-volume model
    'gemini-1.5-pro',
    'gemini-pro' # Legacy Fallback
]



def generate_content_with_retry(content_payload):
    # SELF-HEALING: If AI seems offline, try to find the key one last time
    if not is_ai_ready():
        print("⚠️ AI Logic State check failed. Attempting Emergency Key Reload...")
        reload_keys()
        
    if not is_ai_ready():
        return "System Alert: AI Disconnected. Please check if your API Key is valid and saved in .env"

    last_error = ""

    # --- STRICT PAYLOAD NORMALIZATION ---
    formatted_contents = []
    try:
        parts = []
        if isinstance(content_payload, str):
            parts.append(types.Part.from_text(text=content_payload))
        elif isinstance(content_payload, list):
            for item in content_payload:
                if isinstance(item, str):
                    parts.append(types.Part.from_text(text=item))
                elif isinstance(item, dict) and "data" in item:
                    img_bytes = base64.b64decode(item['data'])
                    parts.append(types.Part.from_bytes(data=img_bytes, mime_type=item.get('mime_type', 'image/jpeg')))
                elif hasattr(item, 'save'): 
                    buf = io.BytesIO()
                    item.save(buf, format='JPEG')
                    parts.append(types.Part.from_bytes(data=buf.getvalue(), mime_type='image/jpeg'))

        if not parts: raise Exception("No valid content parts found.")
        formatted_contents = [types.Content(role='user', parts=parts)]

    except Exception as e:
        print(f"❌ Payload Formatting Error: {e}")
        return f"System Alert: Error processing input data. {e}"

    # --- EXECUTION LOOP (Smart Fallback) ---
    # Strategy: Try Primary Key with ALL models first (fastest path if key is good but model is busy)
    # Then switch to backup keys.
    
    for key_index, api_key in enumerate(API_KEYS):
        client = None
        try:
            client = genai.Client(api_key=api_key)
        except: continue

        for model_name in MODEL_POOL:
            try:
                # print(f"Trying Key #{key_index+1} with {model_name}...") # Debug noise reduced
                response = client.models.generate_content(
                    model=model_name,
                    contents=formatted_contents
                )
                
                if response and response.text:
                    return response.text.strip()
                
            except Exception as e:
                error_str = str(e)
                last_error = error_str
                
                if "429" in error_str or "Quota" in error_str:
                    print(f"⚠️ QUOTA HIT: Key #{key_index+1} / {model_name}. Waiting 5s...")
                    time.sleep(5) # Increased backoff for 429
                    continue 
                elif "404" in error_str:
                    # Model not found/supported
                    print(f"⚠️ MODEL ERROR: {model_name} not found or not supported in your region. ({error_str})")

                elif "403" in error_str or "key" in error_str.lower():
                     # Key issue
                     pass
                else:
                    print(f"⚠️ API Error: {error_str}")
                    time.sleep(1)

    print("❌ CRITICAL: ALL MODELS & KEYS EXHAUSTED.")
    print(f"❌ LAST ERROR: {last_error}")
    
    if "429" in last_error or "403" in last_error or "key" in last_error.lower():
        return "System Alert: API Key Quota Exceeded. Please try again in a minute or use a new key."
    
    # Catch-all for 404s or other API errors
    return f"System Alert: AI Connection Failed. Last Error: {last_error}"
