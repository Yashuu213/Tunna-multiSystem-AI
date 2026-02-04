
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

print("DEBUG: Sending request to OpenRouter...")
# Try a very standard model
model = "google/gemini-2.0-flash-001" 

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/Yashuu213/Tunna-multiSystem-AI",
    "X-Title": "Tuuna AI", 
}
payload = {
    "model": model, 
    "messages": [{"role": "user", "content": "Hi"}]
}

try:
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=10
    )
    
    with open("debug_response.txt", "w") as f:
        f.write(f"Status: {resp.status_code}\n")
        f.write(f"Headers: {resp.headers}\n")
        f.write(f"Body: {resp.text}\n")
    
    print("Done. Check debug_response.txt")
    
except Exception as e:
    with open("debug_response.txt", "w") as f:
        f.write(f"Exception: {e}")
    print(f"Exception: {e}")
