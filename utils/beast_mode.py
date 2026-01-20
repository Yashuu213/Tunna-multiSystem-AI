
import os
import json
import subprocess
import webbrowser
import time
import pyperclip
from duckduckgo_search import DDGS
from .ai_config import generate_content_with_retry

def execute_python_code(code_str):
    """Writes and executes a dynamic Python script."""
    try:
        print("⚡ GOD MODE: Executing dynamic script...")
        
        # Clean code (remove markdown fences)
        code_str = code_str.replace("```python", "").replace("```", "").strip()
        
        filename = "god_mode_task.py"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code_str)
            
        # Execute
        result = subprocess.run(f"python {filename}", shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        
        # Auto-Heal: Check for missing modules
        if "ModuleNotFoundError" in output:
            try:
                mod_name = output.split("No module named '")[1].split("'")[0]
                print(f"💊 Auto-Healing: Installing missing module '{mod_name}'...")
                subprocess.run(f"pip install {mod_name}", shell=True)
                # Retry
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
