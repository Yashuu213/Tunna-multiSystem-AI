#!/bin/bash

echo "========================================"
echo "  TUUNA AI - macOS Build Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found! Please install Python 3.10+ first."
    exit 1
fi

echo "[1/4] Installing dependencies..."
pip3 install -r requirements-macos.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies!"
    exit 1
fi

echo ""
echo "[2/4] Cleaning previous builds..."
rm -rf build dist

echo ""
echo "[3/4] Building executable with PyInstaller..."
pyinstaller tuuna.spec --clean --noconfirm --windowed
if [ $? -ne 0 ]; then
    echo "[ERROR] Build failed!"
    exit 1
fi

echo ""
echo "[4/4] Copying .env template..."
if [ ! -f "dist/TuunaAI.app/Contents/MacOS/.env" ]; then
    cat > dist/TuunaAI.app/Contents/MacOS/.env << EOF
# Tuuna AI Configuration
GOOGLE_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=
EOF
fi

echo ""
echo "========================================"
echo "  BUILD SUCCESSFUL!"
echo "========================================"
echo ""
echo "Application location: dist/TuunaAI.app"
echo ""
echo "To run: Open TuunaAI.app from Finder"
echo "Or: open dist/TuunaAI.app"
echo ""
