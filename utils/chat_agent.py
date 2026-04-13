import time
import json
import threading
import pyautogui
from .ai_config import generate_content_with_retry
from .vision import get_screenshot, get_dpi_scaling

# Global State
CHATTING_ACTIVE = False
CHATTING_THREAD = None
CHAT_CONTEXT = ""

def auto_chat_loop_thread(target_name):
    """
    Background thread that watches a chat window and replies autonomously.
    """
    global CHATTING_ACTIVE, CHAT_CONTEXT, pyautogui
    print(f"🗨️ Tunna Companion: STARTED. Chatting with '{target_name}'...")
    
    last_processed_reply = ""
    
    while CHATTING_ACTIVE:
        try:
            # 1. Capture State
            screenshot = get_screenshot()
            if not screenshot:
                time.sleep(5)
                continue
                
            # 2. Vision Analysis
            scale_x, scale_y = get_dpi_scaling()
            width, height = pyautogui.size()
            phys_w, phys_h = int(width * scale_x), int(height * scale_y)
            
            prompt = f"""
            Identify the state of this chat with "{target_name}".
            1. Is the chat window for "{target_name}" active? 
            2. If YES: 
               - If there are NO messages yet, or the last message was from THEM, suggest a friendly opening/reply.
               - If the last message was from ME, but I want to say something else to start, suggest it.
               - RETURN coordinates [x,y] for the bottom 'Type a message' input box.
               - SET "status": "REPLY".
            3. If NO: Provide coordinates for the 'Search' box and SET "status": "SEARCH".
            
            OUTPUT JSON ONLY:
            {{
                "status": "REPLY" | "WAITING" | "SEARCH",
                "last_message": "...",
                "reply": "Friendly message (Context: {CHAT_CONTEXT})",
                "click_x": <coordinate>,
                "click_y": <coordinate>
            }}
            
            Resolution: {phys_w}x{phys_h}
            """
            
            try:
                print(f"🗨️ Companion: Analyzing chat state (Target: {target_name})...")
                text = generate_content_with_retry([prompt, screenshot])
                
                if "{" in text and "}" in text:
                    start = text.find("{")
                    end = text.rfind("}") + 1
                    data = json.loads(text[start:end])
                    
                    status = data.get("status", "WAITING")
                    msg = data.get("last_message", "Unknown")
                    reply = data.get("reply", "")
                    cx_phys = data.get("click_x")
                    cy_phys = data.get("click_y")
                    
                    print(f"   [STATE] Status: {status} | Last Msg: {msg}")

                    if status == "SEARCH" and cx_phys and cy_phys:
                        print(f"🔍 Companion: Search mode triggered at ({cx_phys}, {cy_phys})")
                        x, y = int(cx_phys / scale_x), int(cy_phys / scale_y)
                        pyautogui.click(x, y)
                        time.sleep(1)
                        pyautogui.write(target_name, interval=0.1)
                        time.sleep(1)
                        pyautogui.press('enter')
                        print("✅ Search executed.")

                    elif status == "REPLY" and reply:
                        # Success condition: either it's a new incoming message, or if it's the start of the chat (no previous messages)
                        is_new_msg = (msg != last_processed_reply)
                        is_empty_chat = (msg == "Unknown" or msg == "")
                        
                        if is_new_msg or is_empty_chat:
                            print(f"📩 Action Triggered: '{reply}'")
                            if cx_phys and cy_phys:
                                x, y = int(cx_phys / scale_x), int(cy_phys / scale_y)
                                # Human Delay
                                time.sleep(3)
                                pyautogui.click(x, y)
                                time.sleep(0.5)
                                if is_empty_chat: last_processed_reply = "INIT_SENT"
                                else: last_processed_reply = msg
                                
                                pyautogui.write(reply, interval=0.05)
                                pyautogui.press('enter')
                                
                                CHAT_CONTEXT += f"\nMe: {reply}"
                                print("✅ Message Sent.")
                            else:
                                print("⚠️ Error: AI suggested REPLY but gave no coordinates.")
                        else:
                            print("⏳ Companion: Waiting for their move...")
                    else:
                        print(f"ℹ️ Companion: {status} - No action taken.")
                        
                else:
                    print("⚠️ Companion: AI returned text without JSON. Response was too long or invalid.")
                    
            except Exception as e:
                print(f"❌ Companion Vision Error: {e}")
                
        except Exception as e:
            print(f"❌ Companion Loop Crash: {e}")
            
        time.sleep(10) # Check every 10 seconds to save API quota

    print("🗨️ Tunna Companion: STOPPED.")

def start_chat_mode(target_name):
    global CHATTING_ACTIVE, CHATTING_THREAD, CHAT_CONTEXT
    if CHATTING_ACTIVE: return "Companion mode is already active."
    
    CHATTING_ACTIVE = True
    CHAT_CONTEXT = f"Chatting with {target_name} initiated."
    CHATTING_THREAD = threading.Thread(target=auto_chat_loop_thread, args=(target_name,), daemon=True)
    CHATTING_THREAD.start()
    return f"🗨️ Tunna Companion ACTIVATED. I'll keep chatting with '{target_name}'. Keep the window visible!"

def stop_chat_mode():
    global CHATTING_ACTIVE
    CHATTING_ACTIVE = False
    return "🗨️ Tunna Companion DEACTIVATED."
