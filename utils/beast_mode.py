
import os
import json
import subprocess
import webbrowser
import time
try:
    import pyperclip
except ImportError:
    pyperclip = None
from duckduckgo_search import DDGS
from .ai_config import generate_content_with_retry
from .vision import get_screenshot
from .system_tools import APP_PATHS, run_terminal_command, perform_web_search, find_and_open_file

# Global Callback for logging to UI
LOG_CALLBACK = None

def set_log_callback(func):
    global LOG_CALLBACK
    LOG_CALLBACK = func

def _log(log_type, msg):
    if LOG_CALLBACK:
        LOG_CALLBACK(log_type, msg)
    print(f"[{log_type.upper()}] {msg}")


def execute_python_code(code_str):
    """Writes and executes a dynamic Python script in a Docker Sandbox."""
    try:
        print("⚡ GOD MODE: Preparing Sandboxed Execution...")
        
        # Clean code (remove markdown fences)
        code_str = code_str.replace("```python", "").replace("```", "").strip()
        
        filename = "god_mode_task.py"
        cwd = os.getcwd()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code_str)

        # Check for Docker
        has_docker = False
        try:
            subprocess.run(["docker", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            has_docker = True
        except:
            has_docker = False

        if has_docker:
            print("📦 CONTAINER: Running in secure Docker sandbox...")
            # Sandbox Config
            TIMEOUT = 30 # seconds
            CPU_LIMIT = "0.5" # 50% of 1 CPU
            RAM_LIMIT = "512m" # 512MB RAM
            IMAGE = "python:3.9-slim"
            
            # Base Command
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{cwd}:/app",
                "-w", "/app",
                f"--cpus={CPU_LIMIT}",
                f"--memory={RAM_LIMIT}",
                IMAGE,
                "python", filename
            ]

            try:
                result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=TIMEOUT)
                output = result.stdout + result.stderr
                
                # Auto-Heal (Docker Version)
                if "ModuleNotFoundError" in output:
                    try:
                        mod_name = output.split("No module named '")[1].split("'")[0]
                        print(f"💊 Auto-Healing (Sandbox): Installing '{mod_name}'...")
                        
                        # Re-run with install
                        heal_cmd = [
                            "docker", "run", "--rm",
                            "-v", f"{cwd}:/app",
                            "-w", "/app",
                            f"--cpus={CPU_LIMIT}",
                            f"--memory={RAM_LIMIT}",
                            IMAGE,
                            "/bin/bash", "-c", f"pip install {mod_name} && python {filename}"
                        ]
                        result = subprocess.run(heal_cmd, capture_output=True, text=True, timeout=TIMEOUT + 30)
                        output = result.stdout + result.stderr
                    except Exception as he:
                        output += f"\n[Auto-Heal Failed: {he}]"

                return f"Sandbox Result:\n{output[:2000]}"

            except subprocess.TimeoutExpired:
                return f"Sandbox Error: Execution timed out ({TIMEOUT}s)."
            except Exception as e:
                return f"Sandbox Error: {e}"

        else:
            # Fallback to Host Execution
            print("⚠️ DOCKER NOT FOUND: Running on HOST (Unsafe)...")
            result = subprocess.run(f"python {filename}", shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
            
            # Auto-Heal (Host Version)
            if "ModuleNotFoundError" in output:
                try:
                    mod_name = output.split("No module named '")[1].split("'")[0]
                    print(f"💊 Auto-Healing: Installing missing module '{mod_name}'...")
                    subprocess.run(f"pip install {mod_name}", shell=True)
                    result = subprocess.run(f"python {filename}", shell=True, capture_output=True, text=True)
                    output = result.stdout + result.stderr
                except:
                    pass
                    
            return f"Execution Result:\n{output[:2000]}" 

    except Exception as e:
        return f"Execution Failed: {e}"

def execute_architect(project_name, description):
    """Builds a complete web project instantly."""
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        project_dir = os.path.join(desktop, project_name.replace(" ", "_"))
        
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
            
        print(f"🏗️ Architect: Building '{project_name}'...")
        
        prompt = f"""
        You are an expert Full Stack Developer.
        Create a Modern, Premium, Responsive web project for: "{description}".
        
        Return a JSON object with the code for these 3 files:
        - index.html (Modern HTML5, Tailwind or Custom CSS classes)
        - style.css (Beautiful, Glassmorphism, Dark Mode, Animations)
        - script.js (Interactive logic)
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "index.html": "<!DOCTYPE html>...",
            "style.css": "body {{ ... }}",
            "script.js": "console.log(...)"
        }}
        """
        
        text = generate_content_with_retry(prompt)
        
        start = text.find("{")
        end = text.rfind("}") + 1
        code_data = json.loads(text[start:end])
        
        for filename, content in code_data.items():
            with open(os.path.join(project_dir, filename), "w", encoding="utf-8") as f:
                f.write(content)
                
        index_path = os.path.join(project_dir, "index.html")
        webbrowser.open(f"file:///{index_path}")
        subprocess.run(f"code \"{project_dir}\"", shell=True)
        
        return f"Architect Built '{project_name}'. Opened in Browser & VS Code."
        
    except Exception as e:
        return f"Architect Failed: {e}"

def execute_protocol(protocol_type):
    """System-wide macro for Gaming or Focus."""
    try:
        protocol_type = protocol_type.lower()
        commands = []
        msg = ""

        if "gaming" in protocol_type:
            commands = [
                "taskkill /f /im code.exe",
                "taskkill /f /im teams.exe",
                "taskkill /f /im slack.exe",
                "taskkill /f /im chrome.exe",
                "start steam",
                "start discord"
            ]
            msg = "Gaming Protocol Initiated 🎮. Work apps killed."
            
        elif "focus" in protocol_type:
            commands = [
                "taskkill /f /im steam.exe", 
                "taskkill /f /im discord.exe",
                "taskkill /f /im whatsapp.exe",
                "code" 
            ]
            webbrowser.open("https://www.youtube.com/watch?v=jfKfPfyJRdk") 
            msg = "Focus Protocol Initiated 🧠. Distractions eliminated."
            
        else:
            return "Unknown Protocol. Available: 'gaming', 'focus'."

        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True)
            except: pass
            
        return msg

    except Exception as e:
        return f"Protocol Failed: {e}"

def execute_job_hunter(role):
    """Automates Job Search and Cover Letter prep."""
    try:
        print(f"🏹 Job Hunter: Hunting for '{role}' roles...")
        role_lower = role.lower()
        
        only_linkedin = False
        search_keyword = role
        
        if "linkedin" in role_lower:
            only_linkedin = True
            search_keyword = role_lower.replace("on linkedin", "").replace("linkedin", "").strip()
            print(f"🎯 Specific Platform Detected: LinkedIn Only (Keyword: {search_keyword})")
        
        linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={search_keyword}&f_AL=true"
        webbrowser.open(linkedin_url)
        opened_count = 1
        
        if not only_linkedin:
            query = f"{role} jobs hiring now"
            try:
                results = DDGS().text(query, max_results=4)
                if results:
                    for r in results:
                        webbrowser.open(r['href'])
                        opened_count += 1
                        time.sleep(0.5)
            except:
                print("DuckDuckGo Search failed but LinkedIn is open.")
            
        prompt = f"""
        Write a professional, enthusiastic Cover Letter for a "{search_keyword}" position.
        The candidate is skilled, passionate, and ready to start.
        Keep it generic enough to paste into any application, but specific to the role.
        Do not include placeholders like [Your Name] in the middle, sign it as "A Passionate Developer".
        """
        
        cover_letter = generate_content_with_retry(prompt)
        pyperclip.copy(cover_letter)
        
        return f"Job Hunter: Opened {opened_count} jobs. Copied Cover Letter to Clipboard. Go apply! 🚀"
        
    except Exception as e:
        return f"Job Hunter Failed: {e}"

def execute_cognitive_chain(goal):
    """
    Advanced Multi-Step Reasoning Loop (ReAct v2.0). 
    Features: Reflection, Log Analysis, and Resolution-Aware Clicking.
    """
    from .vision import get_dpi_scaling
    try:
        print(f"🧠 Cognitive Chain: Starting task '{goal}'...")
        history = []
        max_steps = 15 # Increased for complex tasks
        
        for step in range(max_steps):
            print(f"🧠 [REASONING] Step {step+1}/{max_steps}...")
            
            # 1. Capture State (Screen + History)
            screenshot = get_screenshot()
            
            # 2. Construct Expert Brain Prompt
            prompt = f"""
            You are the TUUNA COGNITIVE CORE.
            GOAL: {goal}
            
            PREVIOUS ACTIONS & RESULTS:
            {json.dumps(history[-3:], indent=2) if history else "Start of task."}
            
            INSTRUCTIONS:
            - Analyze the screen and history.
            - If something failed, check the logs or try a different approach.
            - REFLECTION: Why did the previous step succeed/fail? What is missing?
            
            AVAILABLE TOOLS:
            - LOOK: Describe physical screen state.
            - OPEN: Open app/URL. Target: "notepad", "https://google.com".
            - CLICK: Click text/icon. Target: "Login Button".
            - TYPE: Type text. Target: "Data to enter".
            - SCROLL: Scroll down.
            - SEARCH: DDG Search. Target: "Query".
            - READ_LOG: Read system crash logs. Target: "CRASH_LOG.txt".
            - TERMINAL: Run shell command. Target: "dir", "pip list".
            - FINISH: Task done. Target: "Final summary".
            
            OUTPUT JSON ONLY:
            {{
                "reflection": "Last click didn't change the screen, likely missed the button.",
                "thought": "I will try to search for the specific menu item instead.",
                "tool": "SEARCH",
                "target": "..."
            }}
            """
            
            try:
                response = generate_content_with_retry([prompt, screenshot])
                start = response.find("{")
                end = response.rfind("}") + 1
                action_data = json.loads(response[start:end])
                
                reflection = action_data.get("reflection", "No reflection.")
                thought = action_data.get("thought", "")
                tool = action_data.get("tool", "").upper()
                target = action_data.get("target", "")
                
                _log("reflection", reflection)
                _log("thought", thought)
                _log("action", f"{tool} -> {target}")
                
                result = "Executed."
                
                # 3. Execution Engine
                if tool == "FINISH":
                    return f"Mission Accomplished: {target}"
                
                elif tool == "READ_LOG":
                    log_path = os.path.join(os.getcwd(), target)
                    if os.path.exists(log_path):
                        with open(log_path, 'r', encoding='utf-8') as f:
                            result = f"LOG CONTENT:\n{f.read()[-1000:]}" # Last 1000 chars
                    else:
                        result = "Log file not found."
                        
                elif tool == "TERMINAL":
                    result = run_terminal_command(target)

                elif tool == "LOOK":
                    result = f"Observation Summary: {thought}"
                    
                elif tool == "OPEN":
                    if target.startswith("http"):
                        webbrowser.open(target)
                        result = f"Opened Website: {target}"
                    elif target in APP_PATHS:
                         subprocess.Popen(APP_PATHS[target], shell=True)
                         result = f"Opened App: {target}"
                    else:
                        import pyautogui
                        pyautogui.press('win')
                        time.sleep(0.5)
                        pyautogui.write(target)
                        time.sleep(0.5)
                        pyautogui.press('enter')
                        result = f"Launched: {target}"
                    time.sleep(3) # Wait for UI
                    
                elif tool == "CLICK":
                    import pyautogui
                    width, height = pyautogui.size()
                    # Re-normalize for physical coordinates the LLM sees
                    scale_x, scale_y = get_dpi_scaling()
                    phys_w, phys_h = int(width * scale_x), int(height * scale_y)
                    
                    click_prompt = f"""
                    UI Target: "{target}"
                    Resolution: {phys_w}x{phys_h}
                    Return center [x, y] of "{target}".
                    JSON: {{"x": 10, "y": 20}}
                    """
                    coords_res = generate_content_with_retry([click_prompt, screenshot])
                    try:
                        c_start = coords_res.find("{")
                        c_end = coords_res.rfind("}") + 1
                        coords = json.loads(coords_res[c_start:c_end])
                        # Normalize back to logical for PyAutoGUI
                        x = int(coords['x'] / scale_x)
                        y = int(coords['y'] / scale_y)
                        pyautogui.moveTo(x, y, duration=0.6)
                        pyautogui.click()
                        result = f"Clicked '{target}' at logical ({x}, {y})"
                    except:
                        result = f"Target '{target}' not found on screen."

                elif tool == "TYPE":
                    pyperclip.copy(target)
                    import pyautogui
                    pyautogui.hotkey('ctrl', 'v')
                    result = f"Input typed: {target}"
                    
                elif tool == "SCROLL":
                    import pyautogui
                    pyautogui.scroll(-600)
                    result = "Moved view down."
                    
                elif tool == "SEARCH":
                    result = perform_web_search(target)
                    
                else:
                    result = f"Unknown core module: {tool}"

                history.append({
                    "step": step+1, 
                    "thought": thought, 
                    "reflection": reflection,
                    "tool": tool, 
                    "result": result
                })
                time.sleep(1.5)
                
            except Exception as e:
                print(f"Chain Stall: {e}")
                history.append({"step": step+1, "error": str(e)})
        
        return "Cognitive limit reached. Goal partially completed or timed out."
        
    except Exception as e:
        return f"Core Intelligence Failure: {e}"
