import os
import requests
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from groq import Groq

# --- 1. GROQ FALLBACK (Text & Vision) ---
def ask_groq(prompt, image_data=None):
    """
    Fallback to Groq Cloud (Llama 3).
    Supports ultra-fast Vision via llama-3.2-11b-vision-preview!
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️ Groq Fallback Skipped: GROQ_API_KEY not found.")
        return None

    if image_data:
        models_to_try = ["llama-3.2-11b-vision-preview", "llama-3.2-90b-vision-preview"]
    else:
        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768"
        ]
    
    for model in models_to_try:
        try:
            print(f"🚀 Engaging Groq Fallback ({model})...")
            
            if image_data:
                messages = [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt if prompt else "Describe this image."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }]
            else:
                messages = [{"role": "user", "content": prompt}]

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": messages
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 401:
                print(f"❌ Groq Auth Error: Invalid API Key.")
                return None
                
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except Exception as e:
            if "401" in str(e):
                print(f"❌ Groq Auth Error: Invalid API Key.")
                return None 
            print(f"❌ Groq ({model}) Failed: {e}")
            
    return None

# --- 2. OPENROUTER FALLBACK (Full Vision & Features) ---
def ask_openrouter(prompt, image_data=None):
    """
    Primary Fallback to OpenRouter Free Tier.
    Supports VISION (Images) and Full System Prompts.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️ OpenRouter Fallback Skipped: OPENROUTER_API_KEY not found.")
        return None

    # CONFIRMED FREE MODELS (Verified Live)
    # 1. Vision Candidates (Try these first if image exists)
    vision_models = [
        "google/gemini-2.0-pro-exp-02-05:free", 
        "qwen/qwen-vl-plus:free"
    ]
    
    # 2. Text Powerhouses (Verified Survivors)
    text_models = [
        "google/gemini-2.0-pro-exp-02-05:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1:free",
        "arcee-ai/trinity-large-preview:free"
    ]

    print("🚀 Engaging OpenRouter Fallback System...")

    # A. VISION ATTEMPT
    if image_data:
        print(f"👁️ Vision Data Detected ({len(image_data)} bytes) -> Trying Vision Models...")
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt if prompt else "Describe this image."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        }]
        
        for model in vision_models:
            res = _send_openrouter_request(api_key, model, messages)
            if res: return res
            
        print("⚠️ All Vision Models Failed. Dropping Image to attempt Text Fallback...")


    # B. TEXT ATTEMPT (Graceful Degradation)
    # If vision failed (or no image), we use generic prompt with top text models
    messages = [{"role": "user", "content": prompt if prompt else "Hello."}]
    
    for model in text_models:
        res = _send_openrouter_request(api_key, model, messages)
        if res: return res

    print("⚠️ OpenRouter All Models Failed.")
    return None

def _send_openrouter_request(api_key, model, messages):
    try:
        print(f"   >> Trying OpenRouter Model: {model}...")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Tuuna-AI", 
                "X-Title": "Tuuna AI", 
            },
            json={
                "model": model, 
                "messages": messages
            },
            timeout=15 
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                if content:
                    print(f"   ✅ Success! ({len(content)} chars)")
                    return content
        elif response.status_code == 429:
            print(f"   ⚠️ Model {model} rate limited (429).")
        elif response.status_code == 404:
             print(f"   ⚠️ Model {model} not found (404).")
        else:
            print(f"   ⚠️ OpenRouter Error {response.status_code}: {response.text[:150]}")
            
    except Exception as e:
        print(f"   ❌ Connection Error with {model}: {e}")
    return None
