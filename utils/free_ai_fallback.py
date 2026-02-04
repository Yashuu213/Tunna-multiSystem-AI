
import os
import requests
from groq import Groq

def ask_groq(prompt):
    """
    Fallback to Groq (Llama3) if Gemini fails.
    Requires GROQ_API_KEY in .env
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️ Groq Fallback Skipped: GROQ_API_KEY not found.")
        return None

    models_to_try = ["llama3-70b-8192", "llama3-8b-8192"]
    
    for model in models_to_try:
        try:
            print(f"🚀 Engaging Groq Fallback ({model})...")
            client = Groq(api_key=api_key)
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            err_str = str(e)
            if "401" in err_str:
                print(f"❌ Groq Auth Error: Invalid API Key. Check .env")
                return None # Don't try other models if key is bad
            print(f"❌ Groq ({model}) Failed: {e}")
            
    return None

def ask_openrouter(prompt):
    """
    Fallback to OpenRouter (Free Tier) if Groq fails.
    Requires OPENROUTER_API_KEY in .env
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️ OpenRouter Fallback Skipped: OPENROUTER_API_KEY not found.")
        return None

    # List of free models to try in order of preference
    # Updated based on standard OpenRouter Free Tier availability
    # We include a paid model (Flash-001) as a last resort since it's very cheap and confirmed working.
    free_models = [
        "google/gemini-2.0-flash-lite-preview-02-05:free",
        "google/gemini-2.0-flash-exp:free",
        "deepseek/deepseek-r1:free", 
        "mistralai/mistral-7b-instruct:free",
        "google/gemini-2.0-flash-001" 
    ]

    print("🚀 Engaging OpenRouter Fallback System...")

    for model in free_models:
        try:
            print(f"   >> Trying OpenRouter Model: {model}...")
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/Yashuu213/Tunna-multiSystem-AI", # Must be a valid public URL
                    "X-Title": "Tuuna AI", 
                },
                json={
                    "model": model, 
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=15 
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    print(f"   ✅ Success with {model}")
                    return content
            elif response.status_code == 404:
                print(f"   ⚠️ Model {model} unavailable (404).")
            elif response.status_code == 429:
                print(f"   ⚠️ Model {model} rate limited.")
            else:
                print(f"   ⚠️ OpenRouter Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Connection Error with {model}: {e}")

    print("❌ All OpenRouter Free Models failed.")
    return None
