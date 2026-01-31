
import PyInstaller.__main__
import os
import shutil

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
    
    # Hidden Imports (Critical for Flask/Scipy etc)
    '--hidden-import=flask_cors',
    '--hidden-import=pyautogui',
    '--hidden-import=engineio',
    '--hidden-import=socketio',
    '--hidden-import=cv2',
    '--hidden-import=numpy',
    '--hidden-import=PIL',
    '--hidden-import=google',
    '--hidden-import=google.genai',
    '--hidden-import=google.generativeai',
]

# --- FORCE COLLECT GOOGLE NAMESPACE ---
from PyInstaller.utils.hooks import collect_all
datas, binaries, hiddenimports = collect_all('google')
args.extend([f'--hidden-import={x}' for x in hiddenimports])
# Flatten datas to add-data format if needed, but usually hidden-import is enough for logic
# For datas, we add them to args if collect_all returns them
for src, dest in datas:
    args.append(f'--add-data={src}{FRAMEWORK_SEP}{dest}')

# Windows Specifics
if os.name == 'nt':
    args.append('--hidden-import=winshell')
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
