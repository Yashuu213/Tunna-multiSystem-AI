#!/bin/bash
# ENABLE ERROR TRAPPING (Stop on first error)
set -e

echo "==================================================="
echo "  TUUNA AI AGENT - LINUX BUILDER"
echo "==================================================="
echo ""

echo "[1/4] Upgrading PIP..."
pip install --upgrade pip

echo "[2/4] Installing Linux Dependencies..."
# CRITICAL: Remove GUI libs that crash on headless systems
# (Ignore errors if not installed)
pip uninstall -y pyautogui pywhatkit opencv-python || true
pip install -r requirements-linux.txt

echo "[3/4] Building Executable..."
# Pure Headless Build (Simpler, less error-prone, no xvfb needed)
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
echo "  (You can Double-Click it or run ./Tuuna_AI_Agent)"
echo "==================================================="
echo ""
read -p "Press ENTER to close this window..."
