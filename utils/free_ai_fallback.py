
import os
import requests
from groq import Groq

# --- 1. GROQ FALLBACK (LPU Inference - Text Only Backup) ---
def ask_groq(prompt):
    """
    Fallback to Groq Cloud (Llama 3) if OpenRouter also fails.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️ Groq Fallback Skipped: GROQ_API_KEY not found.")
        return None

    # Removed deprecated models, focused on stable ones
    models_to_try = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ]
    
    for model in models_to_try:
        try:
            print(f"🚀 Engaging Groq Fallback ({model})...")
            client = Groq(api_key=api_key)
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
            )
            return chat_completion.choices[0].message.content
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

    # CONFIRMED FREE MODELS (Verified Live 2026-02-09)
    # 1. Vision Candidates (Try these first if image exists)
    vision_models = [
        "google/gemini-2.0-flash-lite-preview-02-05:free", 
        "meta-llama/llama-3.2-11b-vision-instruct:free",
        "qwen/qwen-2-vl-7b-instruct:free"
    ]
    
    # 2. Text Powerhouses (Verified Survivors)
    text_models = [
        "tngtech/deepseek-r1t2-chimera:free",  # DeepSeek R1 (Very smart)
        "deepseek/deepseek-r1-0528:free",      # Backup DeepSeek
        "stepfun/step-3.5-flash:free",         # Fast & Reliable
        "upstage/solar-pro-3:free",            # High logic
        "arcee-ai/trinity-large-preview:free"  # Backup
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
            print(f"   ⚠️ OpenRouter Error {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Connection Error with {model}: {e}")
    return None
