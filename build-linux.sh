#!/bin/bash

echo "========================================"
echo "  TUUNA AI - Linux Build Script"
echo "========================================"
echo ""

# Check Python version (need 3.10+)
PYTHON_CMD=""
if command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "[ERROR] Python 3.10+ not found! Please install Python 3.10 or higher."
    exit 1
fi

echo "Using: $PYTHON_CMD ($($PYTHON_CMD --version))"

# Check if tkinter is available (needed for GUI popup)
echo ""
echo "[0/4] Checking dependencies..."
if ! $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    echo "⚠️  WARNING: tkinter not found!"
    echo "    Install with: sudo apt-get install python3-tk"
    echo "    (API key popup will use terminal input instead of GUI)"
    echo ""
fi

echo "[1/4] Installing dependencies..."
$PYTHON_CMD -m pip install -r requirements-linux.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies!"
    exit 1
fi

echo ""
echo "[2/4] Cleaning previous builds..."
rm -rf build dist

echo ""
echo "[3/4] Building executable with PyInstaller..."
$PYTHON_CMD -m PyInstaller tuuna.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "[ERROR] Build failed!"
    exit 1
fi

echo ""
echo "[4/4] Creating .env template..."
if [ ! -f "dist/.env" ]; then
    cat > dist/.env << 'EOF'
# Tuuna AI Configuration
# Leave keys empty - popup will appear on first run
# Get keys from:
#   GEMINI: https://aistudio.google.com/app/apikey
#   GROQ: https://console.groq.com/keys
#   OPENROUTER: https://openrouter.ai/keys

GOOGLE_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=
EOF
fi

# Make executable
chmod +x dist/TuunaAI

echo ""
echo "========================================"
echo "  BUILD SUCCESSFUL!"
echo "========================================"
echo ""
echo "Executable location: dist/TuunaAI"
echo ""
echo "To run: ./dist/TuunaAI"
echo ""
