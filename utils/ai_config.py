
import os
import time
import base64
import io
import sys
from dotenv import load_dotenv

# --- STABLE SDK IMPORT ---
import google.generativeai as genai
from utils.free_ai_fallback import ask_groq, ask_openrouter

# --- ENVIRONMENT SETUP ---
def get_env_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        # Parent of 'utils' is root
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, ".env")

load_dotenv(get_env_path())

def get_all_api_keys():
    keys = []
    if os.getenv("GOOGLE_API_KEY"): keys.append(os.getenv("GOOGLE_API_KEY").strip())
    for i in range(2, 10): 
        key = os.getenv(f"GOOGLE_API_KEY_{i}")
        if key: keys.append(key.strip())
    return keys

API_KEYS = get_all_api_keys()
MODEL_NAME = 'gemini-2.0-flash'
MODEL_POOL = [MODEL_NAME]  # Added for compatibility with main server.py imports

def is_ai_ready():
    """Checks if ANY valid key is present (Gemini, Groq, or OpenRouter)."""
    has_gemini = len(get_all_api_keys()) > 0
    has_groq = bool(os.getenv("GROQ_API_KEY"))
    has_or = bool(os.getenv("OPENROUTER_API_KEY"))
    return has_gemini or has_groq or has_or

def reload_keys():
    global API_KEYS
    load_dotenv(get_env_path(), override=True)
    API_KEYS = get_all_api_keys()

# --- MAIN GENERATION FUNCTION ---
def generate_content_with_retry(content_payload):
    # 1. State Check
    if not is_ai_ready():
        reload_keys()
        if not is_ai_ready():
            return "System Alert: No API Keys found. Please check .env file."

    # 2. Payload Normalization (List/Dict for Stable SDK)
    final_payload = []
    image_b64 = None  # To capture image for fallback

    try:
        if isinstance(content_payload, str):
            final_payload.append(content_payload)
        elif isinstance(content_payload, list):
            for item in content_payload:
                if isinstance(item, str):
                    final_payload.append(item)
                elif isinstance(item, dict) and "data" in item:
                    # Image Blob
                    image_data = base64.b64decode(item['data'])
                    image_b64 = item['data'] # Store for fallback
                    final_payload.append({
                        "mime_type": item.get('mime_type', 'image/jpeg'),
                        "data": image_data
                    })
                elif hasattr(item, 'save'): 
                    # PIL Image
                    buf = io.BytesIO()
                    item.save(buf, format='JPEG')
                    image_bytes = buf.getvalue()
                    image_b64 = base64.b64encode(image_bytes).decode('utf-8') # Store for fallback
                    final_payload.append({
                        "mime_type": "image/jpeg",
                        "data": image_bytes
                    })
    except Exception as e:
        return f"System Alert: Payload Error: {e}"

    last_error = ""

    # 3. Gemini Execution Loop
    if API_KEYS:
        for index, key in enumerate(API_KEYS):
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(MODEL_NAME)
                response = model.generate_content(final_payload)
                
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                err = str(e)
                last_error = err
                if "429" in err or "Quota" in err:
                    time.sleep(2) # Short wait, then try next key
                    continue
                # If 404/Other, try next key just in case

    print(f"⚠️ Primary Gemini Failed. Last Error: {last_error}")

    # 4. Fallback Protocol (Universal Backup Brain)
    fallback_text = ""
    for item in final_payload:
        if isinstance(item, str): fallback_text += item + " "
    
    # Trigger fallback if text OR image exists
    if fallback_text or image_b64:
        print("🔄 Initiating Fallback...")
        
        # A. Try OpenRouter (Gemini Flash Lite) - Vision Supported
        if os.getenv("OPENROUTER_API_KEY"):
            print("👁️ Engaging OpenRouter Vision Fallback...")
            res = ask_openrouter(fallback_text, image_b64)
            if res: return res
        else:
             print("⚠️ OpenRouter Key Missing - Skipping Vision Fallback.")
            
        # B. Try Groq (Llama 3) - Text Only (Blind)
        if os.getenv("GROQ_API_KEY"):
             print("⚠️ Attempting Groq Blind Fallback (Image ignored if present)...")
             prompt_to_use = fallback_text
             if image_b64 and not prompt_to_use:
                 prompt_to_use = "Analyze the image you were supposed to see (System note: Image could not be transmitted)."
             
             res = ask_groq(prompt_to_use)
             if res: return res

    return f"System Alert: All AI Services Failed. Last Gemini Error: {last_error}. Fallback Failed."
