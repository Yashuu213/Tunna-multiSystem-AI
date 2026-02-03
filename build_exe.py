
import PyInstaller.__main__
import shutil
import sys

# --- FIX RECURSION LIMIT (Common PyInstaller Crash) ---
sys.setrecursionlimit(5000)

# --- CONFIGURATION ---
ENTRY_POINT = "server.py"
APP_NAME = "Tuuna_AI_Agent"
ICON_PATH = "static/favicon.ico" # Use if available, else remove

# --- CLEANUP PREVIOUS BUILD ---
if os.path.exists("dist"): shutil.rmtree("dist")
if os.path.exists("build"): shutil.rmtree("build")

print(f"🚀 Starting Build for {APP_NAME}...")

# --- PYINSTALLER ARGS ---
args = [
    ENTRY_POINT,
    f'--name={APP_NAME}',
    '--onefile', # Single .exe file
    '--clean',
    '--noupx', # Disable UPX compression (Fixes CI crashes)
    
    # Hidden Imports (Critical for Flask/Scipy etc)
    '--hidden-import=flask_cors',
    '--hidden-import=pyautogui',
    '--hidden-import=engineio',
    '--hidden-import=socketio',
    '--hidden-import=google',
    '--hidden-import=google.genai',
    '--hidden-import=google.generativeai',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--hidden-import=numpy',
]

# Windows Specifics
if os.name == 'nt':
    # args.append('--hidden-import=winshell') # PyInstaller finds it automatically from import
    FRAMEWORK_SEP = ';'
else:
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
