
import pyautogui
import threading
import json
import time
import os
import datetime
from .ai_config import generate_content_with_retry

# Global State for Auto-Apply
APPLY_LOOP_ACTIVE = False
APPLY_THREAD = None

def get_screenshot():
    """Captures screen and returns a PIL Image."""
    try:
        return pyautogui.screenshot()
    except Exception as e:
        print(f"Screenshot failed: {e}")
        return None

def take_user_screenshot():
    """Saves SS to Desktop and opens it."""
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Screenshot_{ts}.png"
        filepath = os.path.join(desktop, filename)
        pyautogui.screenshot(filepath)
        os.startfile(filepath)
        return f"Screenshot saved to Desktop: {filename}"
    except Exception as e:
        return f"Screenshot error: {e}"

def omni_vision_action(instruction):
    """General Vision Agent: Find X and Click it."""
    try:
        screenshot = get_screenshot()
        if not screenshot: return "Failed to see screen."
        
        width, height = pyautogui.size()
        prompt = f"""
        Task: {instruction}
        Analyze this UI. Return the center [x, y] of the UI element that achieves the task.
        If the task is to type something, return the coordinates of the input field.
        Image Size: {width}x{height}
        OUTPUT FORMAT (JSON ONLY): {{"x": 123, "y": 456}}
        """
        
        text = generate_content_with_retry([prompt, screenshot])
        
        if "{" in text and "}" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            coords = json.loads(text[start:end])
            
            if "x" in coords and "y" in coords:
                x, y = int(coords['x']), int(coords['y'])
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                return f"Omni-Vision: Clicked at ({x}, {y})"
            return "Omni-Vision: Could not locate target."
        return "Omni-Vision: AI did not return coordinates."
        
    except Exception as e:
        return f"Omni-Vision Error: {e}"

def auto_apply_loop_thread():
    """Background thread for Vision-Based Auto-Applying."""
    global APPLY_LOOP_ACTIVE
    print("🤖 The Closer: Auto-Apply Loop STARTED. Watching for buttons...")
    
    while APPLY_LOOP_ACTIVE:
        try:
            # 1. Capture Screen
            screenshot = get_screenshot()
            if not screenshot:
                time.sleep(3)
                continue
                
            # 2. Vision Analysis
            width, height = pyautogui.size()
            prompt = f"""
            Analyze this UI for Job Application buttons.
            Look for buttons with EXACT text: "Easy Apply", "Next", "Review", "Submit application", "Submit", "Done".
            
            Return the center [x, y] of the MOST important button to progress.
            Prioritize "Easy Apply" first, then "Submit", then "Next".
            
            If NO such button is visible, return {{}}.
            
            Image Size: {width}x{height}
            OUTPUT FORMAT (JSON ONLY): {{"x": 123, "y": 456}}
            """
            
            try:
                print("🤖 Closer: Analyzing Vision...")
                text = generate_content_with_retry([prompt, screenshot])
                print(f"🤖 Closer Raw AI Response: {text[:100]}...") 
                
                if "{" in text and "}" in text:
                    start = text.find("{")
                    end = text.rfind("}") + 1
                    coords = json.loads(text[start:end])
                    
                    if "x" in coords and "y" in coords:
                        x, y = int(coords['x']), int(coords['y'])
                        print(f"🤖 The Closer: FOUND TARGET! Clicking button at ({x}, {y})...")
                        pyautogui.moveTo(x, y, duration=0.5)
                        pyautogui.click()
                        time.sleep(4) 
                    else:
                        print("🤖 Closer: No clickable target found in JSON.")
                        time.sleep(3)
                else:
                    print("🤖 Closer: AI did not return JSON.")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"Closer Vision Error: {e}")
                time.sleep(3)
                
        except Exception as e:
            print(f"Auto Apply Loop Crash: {e}")
            time.sleep(5)
            
    print("🤖 The Closer: Auto-Apply Loop STOPPED.")

def start_auto_apply():
    global APPLY_LOOP_ACTIVE, APPLY_THREAD
    if APPLY_LOOP_ACTIVE: return "Auto-Apply is already running."
    APPLY_LOOP_ACTIVE = True
    APPLY_THREAD = threading.Thread(target=auto_apply_loop_thread, daemon=True)
    APPLY_THREAD.start()
    return "🤖 The Closer STARTED. I am watching for 'Easy Apply' buttons. Keep LinkedIn visible!"

def stop_auto_apply():
    global APPLY_LOOP_ACTIVE
    APPLY_LOOP_ACTIVE = False
    return "🤖 The Closer STOPPED."
