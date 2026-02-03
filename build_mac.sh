#!/bin/bash
# ENABLE ERROR TRAPPING
set -e

# FORCE CD TO SCRIPT DIRECTORY (Fixes "File not found" when dragging script)
cd "$(dirname "$0")"

echo "==================================================="
echo "  TUUNA AI AGENT - MAC OS BUILDER"
echo "==================================================="
echo ""

echo "[1/4] Upgrading PIP..."
pip3 install --upgrade pip

echo "[2/4] Installing Mac Dependencies..."
# Ensure clean env (Remove conflicting GUI libs if presenting)
pip3 uninstall -y pyautogui pywhatkit opencv-python || true
pip3 install -r requirements-mac.txt

echo "[3/4] Building Application..."
python3 build_exe.py

# COPY .ENV (Convenience)
if [ -f .env ]; then
    echo "Copying config..."
    cp .env dist/
fi

# ENSURE EXECUTABLE PERMISSIONS
chmod +x dist/Tuuna_AI_Agent

echo ""
echo "==================================================="
echo "  BUILD COMPLETE!"
echo "  Your App is ready: dist/Tuuna_AI_Agent"
echo "  (Right-Click -> Open to run it)"
echo "==================================================="
echo ""
read -p "Press ENTER to close this window..."
