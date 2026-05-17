# NOVA Packaging Guide (Windows)

This document explains how to package NOVA as a standalone Windows executable using PyInstaller.

## 📋 Prerequisites
1.  **Python 3.8+** installed.
2.  **Tesseract OCR** installed (and path known).
3.  **Visual C++ Redistributable** (usually present on Windows).

## 🛠️ Build Steps

1.  **Activate Virtual Environment**:
    ```powershell
    .\venv\Scripts\activate
    ```

2.  **Install Build Dependencies**:
    ```powershell
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

3.  **Run Build Script**:
    ```powershell
    python build_nova.py
    ```

4.  **Find the Output**:
    - The bundled folder will be in `dist_build/nova/`.
    - The main executable is `dist_build/nova/nova.exe`.

## 🚀 Running the Executable

1.  **Copy Configuration**:
    - Copy `.env.example` to `dist_build/nova/.env`.
    - Edit `dist_build/nova/.env` with your API keys, Tesseract path, and optional microphone overrides.

2.  **Execute Modes**:
    - **Normal Mode**: `.\dist_build\nova\nova.exe`
    - **GUI Mode**: `.\dist_build\nova\nova.exe --gui`
    - **Wake Mode**: `.\dist_build\nova\nova.exe --wake`
    - **Test Mode**: `.\dist_build\nova\nova.exe --test`

## ⚠️ Important Notes
- **Safety Confirmation**: Even as an `.exe`, NOVA will still ask for confirmation before performing desktop actions or saving notes.
- **Fail-safe**: Slapping the mouse to any corner of the screen will still abort automation.
- **Microphone**: Ensure your microphone is connected and recognized by Windows before starting.

## 🔍 Troubleshooting

### 1. "Tesseract is not found"
Ensure `NOVA_TESSERACT_CMD` in your `.env` (beside the `.exe`) points to the correct location of `tesseract.exe`.

### 2. "PyAudio error" or "Microphone not detected" in Packaged EXE
- **Copy Env Configuration**: Make sure the `.env` file containing your microphone settings is placed directly in the `dist_build/nova/` folder beside `nova.exe`.
- **List Audio Devices**: Start `.\dist_build\nova\nova.exe --test` and select option **`[31]`** to list available device indexes. If you find your physical mic at another index (e.g. `2`), set `NOVA_MIC_DEVICE_INDEX=2` in your local `.env`.
- **Driver Accessibility**: Ensure Windows privacy settings permit microphone access and that no other application is locking the audio device exclusively.

### 3. Windows Defender Warning
Since the executable is not digitally signed, Windows Defender may flag it. You may need to click "Run anyway".

### 4. PyQt5 Plugin Errors
If the GUI fails to open with a "Qt platform plugin" error, ensure `PyQt5` is correctly listed in `requirements.txt`.

### 5. Slow Startup
The first startup might be slow as PyInstaller extracts internal libraries to a temporary folder (even in `--onedir` mode).
