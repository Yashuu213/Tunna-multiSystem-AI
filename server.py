# --- CRASH HANDLER (Must be first) ---
import sys
import traceback

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    try:
        with open("CRASH_LOG.txt", "w") as f:
            f.write(error_msg)
    except: pass
    
    print("\n\n" + "="*30)
    print("❌ CRITICAL ERROR OCCURRED ❌")
    print("="*30)
    print(error_msg)
    print("="*30)
    input("\nPress ENTER to exit...")
    sys.exit(1)

sys.excepthook = handle_exception

import os
import json
import time
import random
import threading
import webbrowser
import subprocess
import platform

# --- CRITICAL FIX: macOS OpenSSL Crash ---
os.environ["CRYPTOGRAPHY_OPENSSL_NO_LEGACY"] = "1"

# --- SAFE IMPORTS ---
try:
    import pyautogui
except ImportError:
    print("Warning: pyautogui not found")
    pyautogui = None

try:
    import pywhatkit
except ImportError:
    print("Warning: pywhatkit not found")
    pywhatkit = None

try:
    import pyperclip
except ImportError:
    print("Warning: pyperclip not found")
    pyperclip = None

# --- UTILS IMPORTS ---
try:
    from utils.ai_config import generate_content_with_retry, is_ai_ready, reload_keys, MODEL_POOL
    from utils.system_tools import (
        APP_PATHS, get_system_status, find_and_open_file, write_file, read_file,
        get_clipboard_text, run_terminal_command, perform_web_search, set_alarm,
        save_memory, get_memory_string, learn_lesson
    )
    from utils.organizer import organize_files
    from utils.vision import (
        get_screenshot, take_user_screenshot, omni_vision_action,
        start_auto_apply, stop_auto_apply, capture_webcam_image
    )
    from utils.beast_mode import (
        execute_python_code, execute_architect, execute_protocol,
        execute_job_hunter, execute_cognitive_chain
    )
    print("✅ All Systems Loaded.")
except Exception as e:
    print(f"\n{'!'*50}\n❌ FATAL IMPORT ERROR: {e}\n{'!'*50}")
    input("Press ENTER to exit...")
    sys.exit(1)

winshell = None
if os.name == 'nt':
    try:
        import winshell
    except ImportError:
        pass

# --- LOGGING SYSTEM ---
LOG_BUFFER = []
LOG_LOCK = threading.Lock()

# --- PYINSTALLER RESOURCE PATH ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- FLASK SETUP ---
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__,
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))
CORS(app)

@app.errorhandler(Exception)
def handle_error(e):
    print(f"❌ SERVER ERROR: {e}")
    traceback.print_exc()
    return jsonify({"response": f"System Alert: Internal Server Error.\nDetails: {str(e)}"}), 500

# --- API KEY CHECK (CYBERPUNK UI) ---
def ensure_api_key(force_update=False):
    from dotenv import load_dotenv
    
    try:
        import tkinter as tk
        from tkinter import messagebox
        HAS_UI = True
    except ImportError:
        HAS_UI = False

    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    env_path = os.path.join(base_path, ".env")
    print(f"📂 SECURITY: Loading Config from: {env_path}")
    load_dotenv(env_path)
    
    gemini_key = os.getenv("GOOGLE_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")
    or_key = os.getenv("OPENROUTER_API_KEY", "")

    if (gemini_key or groq_key or or_key) and not force_update:
        return

    print("⚠️ Auth Protocol Initiated...")

    if not HAS_UI:
        print("\n" + "="*40 + "\n   SYSTEM AUTHENTICATION REQUIRED\n" + "="*40)
        new_gemini = input("GEMINI KEY > ").strip()
        new_groq = input("GROQ KEY > ").strip()
        new_or = input("OPENROUTER KEY > ").strip()
        
        content = ""
        if new_gemini: content += f"GOOGLE_API_KEY={new_gemini}\n"
        if new_groq: content += f"GROQ_API_KEY={new_groq}\n"
        if new_or: content += f"OPENROUTER_API_KEY={new_or}\n"
        
        if content:
            with open(env_path, "w") as f:
                f.write(content)
            print("Configuration Saved.")
        return

    # GUI Setup
    BG_COLOR = "#050505"
    PANEL_COLOR = "#0F0F0F"
    ACCENT_COLOR = "#00FF41"
    WARN_COLOR = "#FF0055"
    TEXT_MAIN = "#FFFFFF"
    TEXT_DIM = "#888888"
    
    FONT_HEAD = ("Impact", 18)
    FONT_LABEL = ("Consolas", 10, "bold")
    FONT_INPUT = ("Consolas", 11)

    root = tk.Tk()
    root.title("TUUNA // ACCESS TERMINAL")
    root.configure(bg=BG_COLOR)
    root.overrideredirect(True)
    root.attributes("-topmost", True)

    w, h = 700, 500
    ws, hs = root.winfo_screenwidth(), root.winfo_screenheight()
    x, y = (ws/2) - (w/2), (hs/2) - (h/2)
    root.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

    main_frame = tk.Frame(root, bg=BG_COLOR, highlightbackground=ACCENT_COLOR, highlightthickness=2)
    main_frame.pack(fill="both", expand=True)

    header = tk.Frame(main_frame, bg=BG_COLOR)
    header.pack(fill="x", pady=20)
    
    tk.Label(header, text="NEURAL LINK // CONFIGURATION", font=FONT_HEAD, fg=ACCENT_COLOR, bg=BG_COLOR).pack()
    tk.Label(header, text="CONNECT AVAILABLE AI MODULES BELOW", font=("Arial", 8), fg=TEXT_DIM, bg=BG_COLOR).pack()

    input_frame = tk.Frame(main_frame, bg=BG_COLOR, padx=40)
    input_frame.pack(fill="both", expand=True)

    def create_input_row(parent, label_text, var_value, help_url):
        row = tk.Frame(parent, bg=BG_COLOR, pady=10)
        row.pack(fill="x")
        
        lbl_frame = tk.Frame(row, bg=BG_COLOR)
        lbl_frame.pack(fill="x")
        tk.Label(lbl_frame, text=label_text, font=FONT_LABEL, fg=TEXT_MAIN, bg=BG_COLOR).pack(side="left")
        
        link = tk.Label(lbl_frame, text="[GET KEY]", font=("Arial", 8, "underline"), fg=TEXT_DIM, bg=BG_COLOR, cursor="hand2")
        link.pack(side="right")
        link.bind("<Button-1>", lambda e: webbrowser.open(help_url))

        entry = tk.Entry(row, width=60, font=FONT_INPUT, bg=PANEL_COLOR, fg=ACCENT_COLOR, insertbackground=ACCENT_COLOR, relief="flat")
        entry.insert(0, var_value)
        entry.pack(fill="x", ipady=6, pady=(5, 0))
        tk.Frame(row, height=1, bg=ACCENT_COLOR).pack(fill="x")
        
        return entry

    ent_gemini = create_input_row(input_frame, "PRIMARY CORE (GEMINI)", gemini_key, "https://aistudio.google.com/app/apikey")
    ent_groq = create_input_row(input_frame, "VELOCITY ENGINE (GROQ CLOUD)", groq_key, "https://console.groq.com/keys")
    ent_or = create_input_row(input_frame, "DEEP NET (OPENROUTER)", or_key, "https://openrouter.ai/keys")

    status_label = tk.Label(main_frame, text="WAITING FOR AUTHORIZATION...", font=("Consolas", 9), fg=TEXT_DIM, bg=BG_COLOR)
    status_label.pack(pady=10)

    def submit():
        g_key = ent_gemini.get().strip()
        gr_key = ent_groq.get().strip()
        or_key = ent_or.get().strip()
        
        if not (g_key or gr_key or or_key):
            status_label.config(text="ACCESS DENIED: AT LEAST ONE KEY REQUIRED", fg=WARN_COLOR)
            return

        env_content = ""
        if g_key: 
            os.environ["GOOGLE_API_KEY"] = g_key
            env_content += f"GOOGLE_API_KEY={g_key}\n"
        if gr_key:
            os.environ["GROQ_API_KEY"] = gr_key
            env_content += f"GROQ_API_KEY={gr_key}\n"
        if or_key:
            os.environ["OPENROUTER_API_KEY"] = or_key
            env_content += f"OPENROUTER_API_KEY={or_key}\n"

        try:
            with open(env_path, "w") as f:
                f.write(env_content)
            status_label.config(text="ACCESS GRANTED. INITIALIZING...", fg=ACCENT_COLOR)
            root.after(1000, root.destroy)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
            root.destroy()

    btn_frame = tk.Frame(main_frame, bg=BG_COLOR)
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text=">> INITIALIZE SYSTEMS <<", font=("Arial", 11, "bold"), 
              bg=ACCENT_COLOR, fg="black", activebackground="white", relief="flat", 
              padx=30, pady=10, command=submit).pack()

    tk.Button(main_frame, text="X", font=("Arial", 12), bg=BG_COLOR, fg="#333", 
              relief="flat", command=lambda: sys.exit(0)).place(x=660, y=10)

    root.mainloop()

ensure_api_key()
reload_keys()

# --- ACTION HANDLER (FIXED - SINGLE BLOCK) ---
def execute_ai_action(action_data):
    """Executes the JSON action(s) returned by Gemini."""
    
    if isinstance(action_data, list):
        results = []
        for action_item in action_data:
            result = execute_ai_action(action_item)
            results.append(result)
        return " | ".join(results)

    action = action_data.get("action")
    target = action_data.get("target", "")
    
    print(f"Executing AI Action: {action} -> {target}")

    # 1. DELAY
    if action == "delay":
        try:
            seconds = float(target)
            time.sleep(seconds)
            return f"Waited {seconds}s"
        except:
            time.sleep(1)
            return "Waited 1s"

    # 2. OPEN APP
    elif action == "open_app":
        if target in APP_PATHS:
            os.system(APP_PATHS[target])
            return f"Opening {target}"
        elif pyautogui:
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.write(target)
            time.sleep(0.5)
            pyautogui.press('enter')
            return f"Opening {target}"
        return "Error: pyautogui not available"

    # 3. OPEN WEB
    elif action == "open_web":
        if not target.startswith('http'):
            target = 'https://' + target
        webbrowser.open(target)
        return f"Opening {target}"

    # 4. PLAY MUSIC
    elif action == "play_music":
        if pywhatkit:
            pywhatkit.playonyt(target)
            return f"Playing {target} on YouTube"
        return "Error: pywhatkit not available"

    # 5. WHATSAPP
    elif action == "whatsapp":
        target = str(target)
        message = action_data.get("message", "")
        
        if target.startswith("+"):
            if pywhatkit:
                try:
                    pywhatkit.sendwhatmsg_instantly(target, message, tab_close=True)
                    return f"Sent WhatsApp to {target}: {message}"
                except Exception as e:
                    return f"WhatsApp API Error: {e}"
            return "Error: pywhatkit not available"
        else:
            if not pyautogui:
                return "Error: Visual Mode requires PyAutoGUI."
            
            print(f"⏳ Opening WhatsApp Desktop for '{target}'...")
            # Try opening Desktop App first, fallback to Web if needed
            os.system("start whatsapp:") 
            time.sleep(5) # Wait for app to focus
            
            # Search for Contact (Universal Ctrl+F or Ctrl+N)
            pyautogui.hotkey('ctrl', 'f') 
            time.sleep(1)
            
            pyautogui.write(target, interval=0.1)
            time.sleep(1.5)
            pyautogui.press('down') # Select first result
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1)
            
            if message:
                pyautogui.write(message, interval=0.05)
                time.sleep(0.5)
                pyautogui.press('enter')
                return f"Opened Chat for '{target}' and sent: {message}"
            
            return f"Opened WhatsApp Chat for '{target}'"

    # 6. SYSTEM CONTROL
    elif action == "system":
        if "shutdown" in target:
            os.system("shutdown /s /t 10")
            return "Shutting down in 10s"
        if "restart" in target:
            os.system("shutdown /r /t 10")
            return "Restarting in 10s"
        if "sleep" in target:
            os.system("rundll32.dll powrprof.dll,SetSuspendState 0,1,0")
            return "Going to sleep"
        if "battery" in target:
            return get_system_status() if 'get_system_status' in globals() else "N/A"
        if "alarm" in target:
            return set_alarm(action_data.get("seconds", 5))
        if "recycle" in target:
            if winshell:
                try:
                    winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
                    return "Recycle bin emptied"
                except:
                    return "Recycle bin already empty"
            return "Recycle bin action only available on Windows."
        return f"Unknown system command: {target}"

    # 7. MOUSE CONTROL
    elif action == "mouse":
        if not pyautogui:
            return "Error: pyautogui not available"
        sub = action_data.get("sub")
        if sub == "move":
            amount = 100
            if "up" in target:
                pyautogui.moveRel(0, -amount)
            elif "down" in target:
                pyautogui.moveRel(0, amount)
            elif "left" in target:
                pyautogui.moveRel(-amount, 0)
            elif "right" in target:
                pyautogui.moveRel(amount, 0)
            return "Moved mouse"
        if sub == "click":
            pyautogui.click()
            return "Clicked"
        if sub == "right_click":
            pyautogui.click(button='right')
            return "Right clicked"
        if sub == "scroll":
            if "up" in target:
                pyautogui.scroll(500)
            else:
                pyautogui.scroll(-500)
            return "Scrolled"

    # 8. MEDIA
    elif action == "media":
        sub = action_data.get("sub")
        if sub == "screenshot":
            return take_user_screenshot() if 'take_user_screenshot' in globals() else "N/A"
        if sub == "screen_record":
            duration = int(action_data.get("duration", 10))
            code = f"""
import cv2
import numpy as np
import pyautogui
import time
import os

SCREEN_SIZE = tuple(pyautogui.size())
fourcc = cv2.VideoWriter_fourcc(*"XVID")
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
filename = os.path.join(desktop, f"ScreenRec_{{int(time.time())}}.avi")
out = cv2.VideoWriter(filename, fourcc, 20.0, SCREEN_SIZE)

print(f"Recording for {duration} seconds...")
start_time = time.time()
while int(time.time() - start_time) < {duration}:
    img = pyautogui.screenshot()
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    out.write(frame)
    
out.release()
print(f"Saved: {{filename}}")
os.startfile(filename)
"""
            return execute_python_code(code)
        if sub == "voice_record":
            duration = int(action_data.get("duration", 10))
            code = f"""
import sounddevice as sd
from scipy.io.wavfile import write
import os
import time

fs = 44100
seconds = {duration}
print(f"Recording Voice for {duration}s...")
myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
sd.wait()

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
filename = os.path.join(desktop, f"VoiceRec_{{int(time.time())}}.wav")
write(filename, fs, myrecording)
print(f"Saved: {{filename}}")
os.startfile(filename)
"""
            return execute_python_code(code)

    # 9. KEYBOARD
    elif action == "keyboard":
        if not pyautogui:
            return "Error: pyautogui not available"
        sub = action_data.get("sub")
        if sub == "type":
            # Semantic Typing v4 (Line-by-Line Paste)
            if pyperclip and "\n" in target:
                lines = target.split("\n")
                
                for i, line in enumerate(lines):
                    # Prepare payload: Line + Newline (except potentially last line)
                    # We utilize the natural newline handling of Paste to avoid Auto-Indent triggers
                    payload = line
                    if i < len(lines) - 1:
                        payload += "\n"
                    
                    pyperclip.copy(payload)
                    pyautogui.hotkey('ctrl', 'v')
                    
                    # Human Delay (Thinking time per line)
                    # This gives the illusion of "Slow Typing" while ensuring "Block Paste" safety
                    time.sleep(random.uniform(0.1, 0.4))
                
                return f"Line-Typed {len(lines)} lines"
            else:
                # Single line: Character typing (Safe for Chat/Commands)
                for char in target:
                    pyautogui.write(char)
                    time.sleep(random.uniform(0.01, 0.05)) 
                return f"Typed: {target}"
        if sub == "press":
            pyautogui.press(target)
            return f"Pressed {target}"
        if sub == "copy":
            pyautogui.hotkey('ctrl', 'c')
            return "Copied"
        if sub == "paste":
            pyautogui.hotkey('ctrl', 'v')
            return "Pasted"
        if sub == "hotkey":
            keys = target.split(",")
            pyautogui.hotkey(*[k.strip() for k in keys])
            return f"Pressed Hotkey: {target}"

    # 10. FILES
    elif action == "file":
        sub = action_data.get("sub")
        if sub == "open":
            return find_and_open_file(target)
        if sub == "write":
            return write_file(target, action_data.get("content", ""))
        if sub == "read":
            return read_file(target)

    # 11. MEMORY
    elif action == "memory":
        sub = action_data.get("sub")
        target_val = target
        if sub == "save":
            save_memory(target_val, "user_facts")
        elif sub == "preference":
            save_memory(target_val, "preferences")
        else:
            save_memory(target_val, "user_facts")
        return f"Memory Saved: {target_val}"

    # 12. LEARN
    elif action == "learn":
        learn_lesson(target)
        return f"Lesson Learned: {target}"

    # 13. CLIPBOARD
    elif action == "clipboard":
        return get_clipboard_text()

    # 14. TERMINAL
    elif action == "terminal":
        return run_terminal_command(target)

    # 15. SEARCH
    elif action == "search":
        return perform_web_search(target)

    # 16. ORGANIZE
    elif action == "organize":
        return organize_files(target)

    # 17. BEAST MODE ACTIONS
    elif action == "executor":
        return execute_python_code(action_data.get("code", ""))

    elif action == "architect":
        return execute_architect(target, action_data.get("sub", ""))

    elif action == "protocol":
        return execute_protocol(target)

    elif action == "job_hunter":
        return execute_job_hunter(target)

    elif action == "auto_apply":
        sub = action_data.get("sub")
        if sub == "start":
            return start_auto_apply()
        if sub == "stop":
            return stop_auto_apply()

    elif action == "reasoning":
        return execute_cognitive_chain(target)

    elif action == "vision_agent":
        return omni_vision_action(target)

    return "Action completed."

# --- SYSTEM PROMPT ---
def ask_gemini_brain(user_command, client_image=None):
    """Sends command to Gemini with Auto-Model-Rotation for fallback."""
    
    if not is_ai_ready():
        reload_keys()

    system_prompt = """
You are Tuuna, a friendly and helpful AI personal assistant. You speak in a casual, warm, and engaging tone, like a close friend. You are always ready to help with PC tasks or just chat.

LANGUAGE SUPPORT: You understand both English and Hindi (and Hinglish).
- If the user speaks Hindi, reply in **Hindi (using Devanagari script)** so the TTS engine speaks it correctly.
- Translate Hindi commands to actions (e.g. "Google kholo" -> open_web google).

CODE GENERATION RULES:
- If the user asks to write code or a file, you MUST follow these strict rules:
1. **ghost_writer_mode**: If the user asks to "write code", "type this", or is looking at a code editor, do NOT create a file. Instead, **TYPE/PASTE** the code directly into the active window using the `keyboard` -> `type` action.
2. **file_mode**: Only use `file` -> `write` if the user explicitly says "create a file named..." or "save to...".
3. **NO COMMENTS**: Do not write comments in the code.
4. **NO EXAMPLES**: Do not add "Example usage" blocks.
5. **CLEAN CODE**: Write only the necessary functional code.

Analyze the user's command and decide if it requires a PC action or just a chat response.

If it is a PC ACTION, output ONLY a JSON LIST of objects with this format:
[
    {"action": "open_app", "target": "notepad"},
    {"action": "delay", "target": "2"},
    {"action": "keyboard", "sub": "type", "target": "Hello World"}
]

Available Actions:
- open_app, open_web, play_music
- whatsapp: (Use this for ALL WhatsApp tasks. Target: Name/Phone, Message: Optional)
- media: screenshot, screen_record, voice_record
- system: shutdown, restart, sleep, battery, alarm, recycle_bin
- mouse: move, click, right_click, scroll
- keyboard: type, press, hotkey, copy, paste
- file: open (finds & opens files globally), write (save), read
- architect, protocol, job_hunter, auto_apply
- executor (python code), reasoning, vision_agent

IMPORTANT:
- For WhatsApp, ALWAYS use {"action": "whatsapp", "target": "Name", "message": "Text"}.
- DO NOT use open_app + keyboard for WhatsApp. The specific action handles the UI better.

CURRENT LONG-TERM MEMORY:
{memory_context}

If it is a CHAT/QUESTION, output normal plain text. Do NOT output JSON for chat.

User Command: 
"""
    
    memory_context = get_memory_string()
    final_prompt = system_prompt.replace("{memory_context}", memory_context)
    content_payload = final_prompt + user_command
    
    # Vision check
    vision_keywords = ["look", "see", "screen", "vision", "watch", "display", "monitor", "this", "read"]
    camera_keywords = ["camera", "webcam", "selfie", "hand", "pic", "photo", "me"]
    clipboard_keywords = ["clipboard", "copied", "paste"]
    
    if client_image:
        print("📸 Using Client Webcam Image...")
        content_payload = [final_prompt + user_command, {"mime_type": "image/jpeg", "data": client_image.split(",")[1] if "," in client_image else client_image}]
    elif any(k in user_command.lower() for k in camera_keywords) and "screen" not in user_command.lower():
        print("📸 Camera Request Detected (Webcam)...")
        cam_image = capture_webcam_image()
        if cam_image:
            print("✅ Webcam Image Captured!")
            content_payload = [final_prompt + user_command, cam_image]
        else:
            print("⚠️ Webcam Capture Failed.")
    elif any(k in user_command.lower() for k in vision_keywords):
        print("👀 Vision Request Detected (Screen)...")
        screenshot = get_screenshot() if 'get_screenshot' in globals() else None
        if screenshot:
            content_payload = [final_prompt + user_command, screenshot]
    elif any(k in user_command.lower() for k in clipboard_keywords):
        clip_text = get_clipboard_text()
        content_payload = final_prompt + f"\n[Clipboard Content: {clip_text}]\nUser Command: " + user_command

    try:
        text = generate_content_with_retry(content_payload)
        
        # Parse JSON
        if "[" in text and "]" in text:
            try:
                start = text.find("[")
                end = text.rfind("]") + 1
                action_data = json.loads(text[start:end])
                return action_data, None
            except:
                pass
        
        if "{" in text and "}" in text:
            try:
                start = text.find("{")
                end = text.rfind("}") + 1
                action_data = json.loads(text[start:end])
                return [action_data], None
            except:
                pass

        return None, text
        
    except Exception as e:
        print(f"Server Error: {e}")
        return None, "System Alert: My connection is a bit unstable. Give me a moment."

# --- ROUTES ---
@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"UI Loading Error: {e}. Check templates folder."

@app.route('/health')
def health():
    return "TUUNA AI Server Running"

@app.route('/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command', '').lower()
    client_image = data.get('client_image', None)
    
    print(f"🎤 Received: {command} | Img: {bool(client_image)}")
    
    if not command:
        return jsonify({"response": "I didn't hear anything."})

    actions, response_text = ask_gemini_brain(command, client_image)

    if response_text == "SYSTEM_ALERT_AUTH_ERROR" or (actions and "SYSTEM_ALERT_AUTH_ERROR" in str(actions)):
        return jsonify({"response": "⚠️ SYSTEM ALERT: API Key Quota Exceeded or Invalid.\n\nPlease restart the application to update your key."})
    
    if actions:
        execution_result = execute_ai_action(actions)
        return jsonify({"response": execution_result})
    else:
        return jsonify({"response": response_text})

@app.route('/stream_logs')
def stream_logs():
    global LOG_BUFFER
    with LOG_LOCK:
        logs = list(LOG_BUFFER)
        LOG_BUFFER.clear()
    return jsonify(logs)

# --- MAIN ---
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 TUUNA AI SERVER (BEAST MODE v2.5 FIXED) STARTING...")
    print("="*50)
    
    # Self-test
    print("🔎 Performing AI Logic Self-Test...")
    try:
        if is_ai_ready():
            test_response = generate_content_with_retry("System Check")
            if "System Alert" in test_response or "SYSTEM_ALERT" in test_response:
                print(f"❌ AI SELF-TEST FAILED: {test_response}")
            else:
                print("✅ AI Connection Established. Brain is Online.")
        else:
            print("⚠️ AI Offline: Waiting for API Key...")
    except Exception as e:
        print(f"❌ AI CRITICAL ERROR: {e}")
            
    print("="*50 + "\n")

    # Auto-open browser
    def open_browser():
        time.sleep(1.5)
        url = "http://127.0.0.1:5000"
        opened = False
        
        if platform.system() == "Windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            ]
            for path in chrome_paths:
                if os.path.exists(path):
                    try:
                        subprocess.Popen([path, f"--app={url}"])
                        opened = True
                        break
                    except:
                        pass
        elif platform.system() == "Darwin":
            try:
                subprocess.Popen(["open", "-n", "-a", "Google Chrome", "--args", f"--app={url}"])
                opened = True
            except:
                pass
        elif platform.system() == "Linux":
            try:
                subprocess.Popen(["google-chrome", f"--app={url}"])
                opened = True
            except:
                try:
                    subprocess.Popen(["chromium", f"--app={url}"])
                    opened = True
                except:
                    pass

        if not opened:
            webbrowser.open(url)

    def delayed_launch():
        time.sleep(2.0)
        open_browser()
    
    threading.Thread(target=delayed_launch, daemon=True).start()
    app.run(port=5000, debug=False, use_reloader=False)