@echo off
echo ========================================
echo   TUUNA AI - Windows Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.10+ first.
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements-windows.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo [2/4] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [3/4] Building executable with PyInstaller...
pyinstaller tuuna.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [4/4] Copying .env template...
if not exist "dist\.env" (
    echo # Tuuna AI Configuration > dist\.env
    echo GOOGLE_API_KEY= >> dist\.env
    echo GROQ_API_KEY= >> dist\.env
    echo OPENROUTER_API_KEY= >> dist\.env
)

echo.
echo ========================================
echo   BUILD SUCCESSFUL!
echo ========================================
echo.
echo Executable location: dist\TuunaAI.exe
echo.
echo To run: Double-click TuunaAI.exe
echo.
pause
