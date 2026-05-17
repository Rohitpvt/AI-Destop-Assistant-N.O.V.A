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

## ⚠️ Python Version & Build Environment
Choosing the correct compiler environment and Python release guarantees smooth standalone compilation:
- **Python 3.11 or 3.12 (Recommended / Easiest)**: Precompiled official binary wheels for PyAudio are readily available. Rebuilding the EXE is straightforward.
- **Python 3.14+ (Requires Workaround)**: Precompiled wheels are not uploaded to PyPI. Standard PyAudio will fail during building. Run `pip install PyAudioWPatch` and shim it locally inside `venv/site-packages` as explained in `README.md`.
- **Automatic Bundling**: Our build script **[build_nova.py](file:///C:/Users/rghos/OneDrive - Vivekananda Institute of Professional Studies/PROJECTS/AI Assistant N.O.V.A/build_nova.py)** is pre-configured with the `--hidden-import pyaudiowpatch` and `--hidden-import _portaudiowpatch` flags, ensuring PyInstaller seamlessly extracts and packages compiled `.pyd` PortAudio C-extensions in Python 3.14+ standalone environments.

---

## 🔍 Troubleshooting Standalone Executables

### 1. "Tesseract is not found"
Ensure `NOVA_TESSERACT_CMD` in your `.env` (placed directly beside the `nova.exe`) points to the correct location of `tesseract.exe` (e.g. `C:\Program Files\Tesseract-OCR\tesseract.exe`).

### 2. "PyAudio error" or "Microphone is unavailable" in Standalone EXE
- **Copy Env Configuration**: Make sure your `.env` file containing your microphone settings is placed directly in the `dist_build/nova/` folder beside `nova.exe`.
- **Packaged Diagnostic Test**: Start your packaged binary in terminal mode:
  ```powershell
  .\dist_build\nova\nova.exe --test
  ```
  Select Option **`[31] List available microphones`** to verify your devices are listed. If you need to pin a specific microphone (e.g. index `1`), add `NOVA_MIC_DEVICE_INDEX=1` to the `.env` file *beside `nova.exe`*.
- **Windows Microphone Permissions**: Packaged desktop applications can be blocked by default. Go to **Settings** → **Privacy & security** → **Microphone**, and ensure that **Let desktop apps access your microphone** is turned **On**.
- **Antivirus / Security block**: Some antivirus engines may block compiled PyInstaller executables from opening audio capture streams. Check your quarantine logs or add a temporary exclusion.
- **Rebuilding after changes**: If you add new physical hardware drivers or alter local virtual environment packages, clean and rebuild using:
  ```powershell
  python build_nova.py
  ```

### 3. Windows Defender Warning
Since the executable is not digitally signed, Windows Defender SmartScreen may flag it upon first launch. Click **"More Info"** and then **"Run anyway"**.

### 4. PyQt5 Plugin Errors
If the GUI fails to open with a "Qt platform plugin" error, ensure `PyQt5` is correctly listed in `requirements.txt` and fully installed in your virtual environment before running the build.

