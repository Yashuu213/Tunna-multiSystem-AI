#!/bin/bash
echo "==================================================="
echo "  TUUNA AI AGENT - LINUX BUILDER"
echo "==================================================="
echo ""

echo "[1/4] Upgrading PIP..."
pip install --upgrade pip

echo "[2/4] Installing Linux Dependencies..."
# CRITICAL: Remove GUI libs that crash on headless systems
pip uninstall -y pyautogui pywhatkit opencv-python
pip install -r requirements-linux.txt

echo "[3/4] Checking for Display..."
if ! command -v xvfb-run &> /dev/null
then
    echo "Warning: xvfb-run not found. If this is a headless server, the build might crash."
    echo "Running standard build..."
    python3 build_exe.py
else
    echo "Virtual Display (xvfb) detected. Running in safe mode..."
    xvfb-run python3 build_exe.py
fi

    xvfb-run python3 build_exe.py
fi

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
