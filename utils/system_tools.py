
import os
import subprocess
import shutil
import winshell
import psutil
import pyperclip
import webbrowser
import json
import threading
import time
import winsound
from duckduckgo_search import DDGS

APP_PATHS = {
    "calculator": "calc.exe",
    "notepad": "notepad.exe",
    "paint": "mspaint.exe",
    "cmd": "start cmd",
    "explorer": "explorer.exe",
    "chrome": "start chrome",
    "settings": "start ms-settings:",
    "task manager": "taskmgr",
    "store": "start ms-windows-store:",
    "whatsapp": "start whatsapp:",
}

def get_system_status():
    battery = psutil.sensors_battery()
    percent = battery.percent if battery else "unknown"
    plugged = "plugged in" if battery and battery.power_plugged else "on battery"
    return f"Battery is at {percent} percent and {plugged}."

def find_and_open_file(filename):
    user_dir = os.path.expanduser("~")
    search_dirs = [
        os.path.join(user_dir, "Desktop"),
        os.path.join(user_dir, "Documents"),
        os.path.join(user_dir, "Downloads"),
        os.path.join(user_dir, "Pictures"),
        os.path.join(user_dir, "Videos"),
        os.path.join(user_dir, "Music")
    ]
    print(f"Searching for {filename}...")
    for directory in search_dirs:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['AppData', 'node_modules']]
                for file in files:
                    if filename.lower() in file.lower():
                        file_path = os.path.join(root, file)
                        try:
                            os.startfile(file_path)
                            return f"Opening {file}"
                        except:
                            return f"Found {file} but couldn't open it."
    return f"I couldn't find any file named {filename}."

def write_file(filename, content):
    """Writes content to a file in the current directory."""
    try:
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File created at {filepath}"
    except Exception as e:
        return f"Error writing file: {e}"

def read_file(filename):
    """Reads a file from the current directory."""
    try:
        filepath = os.path.join(os.getcwd(), filename)
        if not os.path.exists(filepath):
             return "File not found in current directory."
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def get_clipboard_text():
    """Reads text from clipboard."""
    try:
        text = pyperclip.paste()
        if not text: return "Clipboard is empty."
        return f"Clipboard Content: {text}"
    except Exception as e:
        return f"Error reading clipboard: {e}"

def run_terminal_command(cmd):
    """Runs a terminal command."""
    try:
        blacklist = ["rm -rf", "format c:", "del /s", "rd /s"]
        if any(b in cmd.lower() for b in blacklist):
            return "Command blocked for safety."
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        return f"Command Output:\n{output[:1000]}" 
    except Exception as e:
        return f"Error running command: {e}"

def perform_web_search(query):
    """Searches the web using DuckDuckGo."""
    try:
        results = DDGS().text(query, max_results=3)
        if not results: return "No results found."
        summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        return f"Search Results for '{query}':\n{summary}"
    except Exception as e:
        return f"Error searching web: {e}"

def set_alarm(seconds):
    try:
        seconds = int(seconds)
        def alarm_thread():
            time.sleep(seconds)
            for _ in range(5):
                winsound.Beep(1000, 500)
                time.sleep(0.5)
            print("⏰ ALARM DONE!")
            
        threading.Thread(target=alarm_thread, daemon=True).start()
        return f"Alarm set for {seconds} seconds."
    except:
        return "Invalid alarm time."

# --- Evolutionary Memory System ---
MEMORY_FILE = "memory.json"

def init_memory():
    if not os.path.exists(MEMORY_FILE):
        default_mem = {
            "user_facts": [],
            "preferences": [],
            "lessons": [],
            "errors": []
        }
        with open(MEMORY_FILE, 'w') as f:
            json.dump(default_mem, f, indent=4)
        return default_mem
    try:
        with open(MEMORY_FILE, 'r') as f:
            data = json.load(f)
            # Migration check
            if isinstance(data, list):
                new_data = {"user_facts": data, "preferences": [], "lessons": [], "errors": []}
                with open(MEMORY_FILE, 'w') as fw:
                    json.dump(new_data, fw, indent=4)
                return new_data
            return data
    except:
        return {"user_facts": [], "preferences": [], "lessons": [], "errors": []}

def save_memory(item, category="user_facts"):
    mem = init_memory()
    if category not in mem: mem[category] = []
    
    if item not in mem[category]:
        mem[category].append(item)
        with open(MEMORY_FILE, 'w') as f:
            json.dump(mem, f, indent=4)
            
    return f"Memory Updated ({category}): {item}"

def learn_lesson(lesson):
    return save_memory(lesson, "lessons")

def get_memory_string():
    mem = init_memory()
    
    context = ""
    if mem["user_facts"]:
        context += "USER FACTS:\n" + "\n".join([f"- {m}" for m in mem["user_facts"]]) + "\n\n"
        
    if mem["preferences"]:
        context += "PREFERENCES:\n" + "\n".join([f"- {m}" for m in mem["preferences"]]) + "\n\n"
        
    if mem["lessons"]:
        context += "LESSONS LEARNED (DO NOT REPEAT MISTAKES):\n" + "\n".join([f"- {m}" for m in mem["lessons"]]) + "\n"
        
    return context.strip() if context else "No memories yet."
