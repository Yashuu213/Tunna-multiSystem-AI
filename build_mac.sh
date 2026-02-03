#!/bin/bash
echo "==================================================="
echo "  TUUNA AI AGENT - MAC OS BUILDER"
echo "==================================================="
echo ""

echo "[1/4] Upgrading PIP..."
pip install --upgrade pip

echo "[2/4] Installing Mac Dependencies..."
pip install -r requirements-mac.txt

echo "[3/4] Building Application..."
python3 build_exe.py

echo ""
echo "==================================================="
echo "  BUILD COMPLETE!"
echo "  Check the 'dist' folder for the executable."
echo "==================================================="
