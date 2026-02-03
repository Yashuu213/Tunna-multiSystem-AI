import PyInstaller.__main__
import shutil
import sys
import os

# --- FIX RECURSION LIMIT (Critical for Windows Build) ---
# --- FIX RECURSION LIMIT (Super-Critical for Windows) ---
sys.setrecursionlimit(20000)

# ... (Configuration lines)

# OS Specific Configuration
if os.name == 'nt':
    # Windows: Force include GUI libs
    args.append('--hidden-import=winshell') 
    args.append('--hidden-import=pyautogui')
    FRAMEWORK_SEP = ';'
else:
    # Linux/Mac: Explicitly EXCLUDE GUI libs to prevent "Headless" crashes
    args.append('--exclude-module=winshell')
    args.append('--exclude-module=pyautogui')
    args.append('--exclude-module=pywhatkit')
    args.append('--exclude-module=pyperclip')
    args.append('--exclude-module=tkinter')
    FRAMEWORK_SEP = ':'

# Add Data Folders (Source;Dest OR Source:Dest based on OS)
args.extend([
    f'--add-data=templates{FRAMEWORK_SEP}templates',
    f'--add-data=static{FRAMEWORK_SEP}static',
    f'--add-data=utils{FRAMEWORK_SEP}utils',
])
    
# Exclude Heavy/Unused Libraries (Optional Optimization)
# args.append('--exclude-module=matplotlib')

args.append('--log-level=WARN')

# Add Icon if exists
if os.path.exists(ICON_PATH):
    args.append(f'--icon={ICON_PATH}')

# --- RUN BUILD ---
PyInstaller.__main__.run(args)

print(f"✅ Build Complete! Check the 'dist' folder for {APP_NAME}.exe")
