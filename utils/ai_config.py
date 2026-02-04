
import os
import time
import base64
import io
from dotenv import load_dotenv
from google import genai
from google.genai import types
from utils.free_ai_fallback import ask_groq, ask_openrouter

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
    """Dynamic check for AI availability (Gemini OR Fallbacks)."""
    # Fix: Also consider Fallback keys as "Ready"
    has_gemini = len(get_all_api_keys()) > 0
    has_groq = bool(os.getenv("GROQ_API_KEY"))
    has_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))
    
    return has_gemini or has_groq or has_openrouter

def get_all_api_keys():
    keys = []
    if os.getenv("GOOGLE_API_KEY"): keys.append(os.getenv("GOOGLE_API_KEY"))
    for i in range(2, 10): 
        key = os.getenv(f"GOOGLE_API_KEY_{i}")
        if key: keys.append(key)
    return keys

API_KEYS = get_all_api_keys()
AI_AVAILABLE = is_ai_ready() # Updated to check all

MODEL_POOL = [
    'gemini-2.0-flash'
]


def validate_models(client):
    """
    Filters MODEL_POOL to only include models actually available to this API key.
    Prevents 404 loops.
    """
    global MODEL_POOL
    try:
        print("🔎 Discovering Available Models...")
        available = {m.name.split("/")[-1] for m in client.models.list()}
        
        valid_models = []
        for requested in MODEL_POOL:
            if requested in available or f"models/{requested}" in available:
                valid_models.append(requested)
            else:
                print(f"⚠️ Model '{requested}' not found in API list - SKIPPING")
        
        if valid_models:
            MODEL_POOL = valid_models
            print(f"✅ Active Model Pool: {MODEL_POOL}")
        else:
            print("❌ No requested models found available! Keeping original pool as fallback.")
            
    except Exception as e:
        print(f"⚠️ Model Discovery Failed: {e}")

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
    
    # FIX: If no Gemini keys, skip directly to fallback logic
    if not API_KEYS:
        print("⚠️ No Gemini Keys found. Skipping directly to Fallback...")
        last_error = "No Primary Keys Configured"
    
    for key_index, api_key in enumerate(API_KEYS):
        client = None
        try:
            client = genai.Client(api_key=api_key)
            if key_index == 0: # Only validate on first key to save time
                validate_models(client)
        except: continue

        for model_name in MODEL_POOL:
            try:
                # print(f"Trying Key #{key_index+1} with {model_name}...") # Debug noise reduced
                response = client.models.generate_content(
                    model=model_name,
                    contents=formatted_contents
                )
                
                if response and hasattr(response, "text") and response.text:
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

    # --- FREE AI FALLBACK SYSTEM ---
    print("\n⚠️ Initiating Fallback Protocol...")
    
    # 1. Extract Text Prompt
    fallback_prompt = ""
    has_image = False
    
    try:
        # Extract from normalized 'formatted_contents'
        for content in formatted_contents:
             for part in content.parts:
                 if part.text:
                     fallback_prompt += part.text + " "
                 if part.inline_data: # If image exists
                     has_image = True
                     
        if has_image:
             fallback_prompt += "\n[System Note: The user also provided an image, but this fallback model cannot see it. Do your best with the text.]"
             
        fallback_prompt = fallback_prompt.strip()
        
    except:
        fallback_prompt = str(content_payload) # Absolute fallback

    if fallback_prompt:
        # 2. Try Groq
        groq_resp = ask_groq(fallback_prompt)
        if groq_resp: 
            print("✅ Groq Fallback Successful.")
            return groq_resp
            
        # 3. Try OpenRouter
        or_resp = ask_openrouter(fallback_prompt)
        if or_resp:
            print("✅ OpenRouter Fallback Successful.")
            return or_resp

    print("❌ Fallback Failed. Returning original error.")

    if "429" in last_error or "403" in last_error or "key" in last_error.lower():
        return "System Alert: API Key Quota Exceeded. Please try again in a minute or use a new key."
    
    # Catch-all for 404s or other API errors
    return f"System Alert: AI Connection Failed. Last Error: {last_error}"
