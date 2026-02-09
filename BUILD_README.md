# 📦 Tuuna AI - Build Instructions

## Quick Start (Windows)

**बस एक command चलाओ:**
```cmd
build-windows.bat
```

यह automatically:
1. ✅ सभी dependencies install करेगा
2. ✅ Executable बनाएगा
3. ✅ `.env` template copy करेगा
4. ✅ `dist/TuunaAI.exe` में ready file देगा

---

## Platform-Specific Instructions

### 🪟 Windows
```cmd
build-windows.bat
```
**Output:** `dist/TuunaAI.exe`

### 🐧 Linux
```bash
chmod +x build-linux.sh
./build-linux.sh
```
**Output:** `dist/TuunaAI`

### 🍎 macOS
```bash
chmod +x build-macos.sh
./build-macos.sh
```
**Output:** `dist/TuunaAI.app`

---

## First Run (API Key Setup)

जब पहली बार executable run करोगे:

1. 🔑 **Popup खुलेगा** - API keys मांगेगा
2. ✍️ **Keys डालो** (कम से कम एक):
   - **GEMINI KEY** (Primary) - [Get Here](https://aistudio.google.com/app/apikey)
   - **GROQ KEY** (Fast Fallback) - [Get Here](https://console.groq.com/keys)
   - **OPENROUTER KEY** (Vision Fallback) - [Get Here](https://openrouter.ai/keys)
3. 💾 **Save होगा** - `.env` file में
4. 🚀 **Server शुरू होगा** - Browser खुलेगा

---

## File Structure After Build

```
dist/
├── TuunaAI.exe          # Main executable
├── .env                 # API keys (auto-created)
└── _internal/           # Dependencies (PyInstaller bundle)
```

---

## Troubleshooting

### Build Failed?
```cmd
# Clean everything and retry
rmdir /s /q build dist
build-windows.bat
```

### Missing Dependencies?
```cmd
pip install -r requirements-windows.txt
```

### API Keys Not Saving?
- Check if `.env` file exists next to the `.exe`
- Make sure you have write permissions

---

## Distribution

**To share with others:**
1. Zip the entire `dist/` folder
2. Share the zip file
3. User extracts and runs `TuunaAI.exe`
4. First run will ask for API keys

**Note:** `.env` file is NOT included in distribution (security). Each user must add their own keys.

---

## Advanced: Manual Build

If you want to customize:

```cmd
# Install PyInstaller
pip install pyinstaller

# Edit tuuna.spec (optional)
notepad tuuna.spec

# Build
pyinstaller tuuna.spec --clean
```

---

## File Sizes (Approximate)

- **Windows:** ~250 MB
- **Linux:** ~220 MB
- **macOS:** ~280 MB (includes .app bundle)

*Large size is normal - includes Python + all libraries*
