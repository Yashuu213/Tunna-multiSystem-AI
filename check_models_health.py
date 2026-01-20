import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("API Key not found!")
    exit()

genai.configure(api_key=api_key)

models_to_test = [
    'gemini-2.0-flash-exp',
    'gemini-2.0-flash', 
    'gemini-1.5-flash',
    'gemini-1.5-flash-8b',
    'gemini-1.5-pro',
    'gemini-1.0-pro'
]

print(f"{'MODEL':<25} | {'STATUS':<10} | {'TIME'}")
print("-" * 50)

for model_name in models_to_test:
    start = time.time()
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hi", request_options={"timeout": 10})
        duration = time.time() - start
        print(f"{model_name:<25} | {'OK':<10} | {duration:.2f}s")
    except Exception as e:
        duration = time.time() - start
        error_msg = str(e)
        status = "ERROR"
        if "404" in error_msg: status = "404 (Not Found)"
        elif "429" in error_msg: status = "429 (Quota)"
        print(f"{model_name:<25} | {status:<10} | {duration:.2f}s")
