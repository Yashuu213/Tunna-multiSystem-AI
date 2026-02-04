
import os
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENROUTER_API_KEY")
print(f"Checking Key: {key[:5]}...{key[-5:] if key else 'None'}")

if not key:
    print("NO KEY FOUND")
    exit()

try:
    print("Fetching available models...")
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {key}"}
    )
    
    if response.status_code == 200:
        models = response.json()['data']
        print(f"Found {len(models)} models.")
        
        print("\n--- FREE MODELS ---")
        free_models = [m['id'] for m in models if 'free' in m['id']]
        for m in free_models:
            print(f"- {m}")
            
        print("\n--- GEMINI MODELS ---")
        gemini = [m['id'] for m in models if 'gemini' in m['id']]
        for m in gemini:
            print(f"- {m}")
            
    else:
        print(f"Error {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
