@echo off
echo ===================================================
echo   TUUNA AI AGENT - WINDOWS BUILDER
echo ===================================================
echo.

echo [1/4] Upgrading PIP...
python -m pip install --upgrade pip

echo [2/4] Installing Windows Dependencies...
pip install -r requirements-win.txt
pip install pyinstaller pywin32 winshell

echo [3/4] Building Executable...
echo [3/4] Building Executable...
python build_exe.py

if exist .env (
    echo Copying config...
    copy .env dist\
)

echo.
echo ===================================================
echo   BUILD COMPLETE!
echo   Your App is ready: dist\Tuuna_AI_Agent.exe
echo ===================================================
pause
