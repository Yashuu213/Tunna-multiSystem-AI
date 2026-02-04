# 🏗️ Build Instructions (Tuuna AI Agent)

Your "Beast Mode" AI Agent is ready for deployment. Follow these steps to create the executable files for Windows, Mac, and Linux.

## 1. Prerequisites
Ensure you have the required libraries installed. Open your terminal in the project folder and run:
```bash
pip install pyinstaller flask google-generativeai groq requests pillow
```
*(Plus your specific OS dependencies like `winshell` for Windows)*

## 2. Building for WINDOWS 🪟
Since you are currently on Windows, this is straightforward.

1.  **Run the Build Script**:
    ```bash
    python build_exe.py
    ```
2.  **Wait**: PyInstaller will analyze your code. This takes 1-3 minutes.
3.  **Locate EXE**: Go to the `dist` folder. You will find `Tuuna_AI_Agent.exe`.
4.  **Test**: Move this EXE to a *new folder* (to simulate a fresh user). Run it.
    *   It should launch valid Flask logs.
    *   It should pop up the **"Neural Access Terminal"** if no `.env` is found.

## 3. Building for MAC / LINUX 🍎🐧
**Note**: You cannot build a Mac app (`.app`) or Linux binary from Windows. You must run the build script *on* a Mac or Linux machine respectively.

1.  **Copy Source**: Copy the entire project folder to your Mac/Linux machine.
2.  **Install Python & Deps**:
    ```bash
    pip install -r requirements.txt
    pip install pyinstaller
    ```
3.  **Run Build**:
    ```bash
    python build_exe.py
    ```
    *The script automatically detects the OS and adjusts flags (e.g., separating paths with `:` instead of `;`).*

4.  **Result**: 
    - **Linux**: You will get a binary in `dist/Tuuna_AI_Agent`.
    - **Mac**: You will get a Unix executable in `dist/Tuuna_AI_Agent`.

## 4. Post-Build Setup (Important)
When you distribute this file to users (or yourself on another PC), remember:
- The **Neural Access Terminal** allows users to enter keys at startup.
- The keys are saved to a `.env` file next to the executable automatically.
- No manual setup required!

---
**Status**:
- ✅ AI Fallback (OpenRouter/Groq) Included.
- ✅ Cyberpunk Auth UI Included.
- ✅ Correct Hidden Imports Configured in `build_exe.py`.
