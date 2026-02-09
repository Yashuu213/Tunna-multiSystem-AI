
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

    # Prioritize Models that are SMART and FREE
    # Added more options and redundancy
    free_models = [
        "google/gemini-2.0-flash-lite-preview-02-05:free", # Primary
        "google/gemini-2.0-flash-exp:free",              # Secondary
        "deepseek/deepseek-r1:free",                     # Backup SOT
        "mistralai/mistral-7b-instruct:free",            # Last Resort
        "google/gemini-2.0-pro-exp-02-05:free"           # Experimental
    ]

    print("🚀 Engaging OpenRouter Fallback System...")

    # Construct Payload (Vision Compatible)
    messages = []
    
    # SYSTEM PROMPT INJECTION (Important for maintaining persona in fallback)
    # Ideally passed from parent, but hardcoded generic here for safety
    
    if image_data:
        print(f"👁️ Vision Data Detected ({len(image_data)} bytes) -> Using Multi-modal Payload")
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt if prompt else "Describe this image."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": prompt if prompt else "Hello."})

    for model in free_models:
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
                timeout=120 # Extended timeout for vision
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
            elif response.status_code == 401:
                print(f"   ❌ OpenRouter Auth Error (401). Check API Key.")
                return None # Stop trying if key is invalid
            else:
                print(f"   ⚠️ OpenRouter Error {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Connection Error with {model}: {e}")

    print("⚠️ OpenRouter All Models Failed.")
    return None
