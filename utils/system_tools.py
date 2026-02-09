
import os
import subprocess
import shutil
import psutil
try:
    import pyperclip
except ImportError:
    pyperclip = None
import webbrowser
import json
import threading
import time
import platform
from duckduckgo_search import DDGS

# --- CROSS-PLATFORM IMPORTS ---
try:
    import winshell
    import winsound
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False

# --- APP PATHS (OS DETECTED) ---
if IS_WINDOWS:
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
else:
    # Mac/Linux Fallbacks (Generic)
    APP_PATHS = {
        "calculator": "open -a Calculator" if platform.system() == "Darwin" else "gnome-calculator",
        "chrome": "open -a 'Google Chrome'" if platform.system() == "Darwin" else "google-chrome",
        "settings": "open -a 'System Preferences'" if platform.system() == "Darwin" else "gnome-control-center",
        "terminal": "open -a Terminal" if platform.system() == "Darwin" else "gnome-terminal",
    }

def get_system_status():
    try:
        battery = psutil.sensors_battery()
        if not battery: return "Battery status unavailable (Desktop?)."
        percent = battery.percent
        plugged = "plugged in" if battery.power_plugged else "on battery"
        return f"Battery is at {percent} percent and {plugged}."
    except:
        return "Could not read system sensors."

def find_and_open_file(filename):
    user_dir = os.path.expanduser("~")
    
    # Smart Directory List based on OS (Recursive Search Scope)
    search_dirs = [
        os.path.join(user_dir, "Desktop"),
        os.path.join(user_dir, "Documents"),
        os.path.join(user_dir, "Downloads"),
        os.path.join(user_dir, "Pictures"),
        os.path.join(user_dir, "Music"),
        os.path.join(user_dir, "Videos")
    ]
    
    print(f"🔎 Global Search Initiated for: '{filename}'...")
    matches = []
    
    for directory in search_dirs:
        if os.path.exists(directory):
            try:
                for root, dirs, files in os.walk(directory):
                    # Smart Skip: Hidden folders and heavy node_modules/venvs
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['AppData', 'node_modules', 'Library', 'venv', 'env', '__pycache__']]
                    
                    for file in files:
                        if filename.lower() in file.lower():
                            full_path = os.path.join(root, file)
                            matches.append(full_path)
            except Exception as e:
                print(f"⚠️ Access Denied: {directory} ({e})")

    if not matches:
        return f"❌ I searched your PC but couldn't find any file named '{filename}'."

    # Remove duplicates if any
    matches = list(set(matches))
    match_count = len(matches)
    
    # Safety Limit: Open max 3 files to prevent system freeze
    files_to_open = matches[:3] 
    opened_log = []
    
    for file_path in files_to_open:
        try:
            print(f"📂 Opening: {file_path}")
            if IS_WINDOWS:
                os.startfile(file_path)
            elif platform.system() == "Darwin": # Mac
                subprocess.call(('open', file_path))
            else: # Linux
                subprocess.call(('xdg-open', file_path))
            opened_log.append(os.path.basename(file_path))
        except Exception as e:
            opened_log.append(f"[Error: {os.path.basename(file_path)}]")

    response = f"✅ Found {match_count} files. Opened: {', '.join(opened_log)}."
    if match_count > 3:
        response += f"\n(Skipped {match_count - 3} others to save memory. Be more specific if needed.)"
    
    return response

def write_file(filename, content):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing file: {e}"

def read_file(filename):
    try:
        if not os.path.exists(filename): return "File not found."
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def get_clipboard_text():
    return pyperclip.paste()

def run_terminal_command(cmd):
    """Runs a terminal command."""
    try:
        blacklist = ["rm -rf", "format", "del /s", "rd /s", "mkfs"]
        if any(b in cmd.lower() for b in blacklist):
            return "Command blocked for safety."
        
        # Cross platform shell execution
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        return f"Command Output:\n{output[:1000]}" 
    except Exception as e:
        return f"Error running command: {e}"

def perform_web_search(query):
    """Searches the web using DuckDuckGo."""
    try:
        results = DDGS().text(query, max_results=3)
        if results:
            summary = ""
            for r in results:
                summary += f"- {r['title']}: {r['href']}\n"
            return f"Search Results for '{query}':\n{summary}"
        return "No results found."
    except Exception as e:
        return f"Search Failed: {e}"

def set_alarm(seconds):
    try:
        seconds = int(seconds)
        def alarm_thread():
            time.sleep(seconds)
            try:
                if IS_WINDOWS:
                    for _ in range(5):
                        winsound.Beep(1000, 500)
                        time.sleep(0.5)
                else:
                    # Mac/Linux Beep
                    print("\a" * 5) # ASCII Bell
            except:
                pass
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
