# N.O.V.A - Next-generation Omniscient Virtual Assistant

NOVA is a high-accuracy, modular AI assistant designed to act as a secure desktop intelligence layer. Inspired by advanced fictional AIs, NOVA combines speech recognition, vision, memory, and automation into a unified, safety-first desktop experience.

## 🌟 Key Features
- **Modern GUI**: A sleek PyQt5 dashboard with live logs and memory previews.
- **Voice Wake Mode**: Listen for "Hey NOVA" to activate.
- **Screen Awareness**: NOVA can "see" your screen using OCR and summarize context.
- **Safe Automation**: Controlled typing, hotkeys, and mouse movements (always requires your "Yes").
- **Long-Term Memory**: Remembers your name, preferences, and past interactions using SQLite.
- **System Monitoring**: Reports on CPU, RAM, Battery, and active windows.

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.8+**
- **Tesseract OCR**: [Download and Install](https://github.com/UB-Mannheim/tesseract/wiki).
- **FFmpeg**: Required for some audio processing.

### 2. Installation
```powershell
git clone https://github.com/Rohitpvt/AI-Destop-Assistant-N.O.V.A.git
cd AI-Destop-Assistant-N.O.V.A
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and fill in your keys:
```env
NVIDIA_API_KEY=your_key_here
NOVA_TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 4. Running NOVA
- **GUI Mode (Recommended)**: `python NOVA/nova.py --gui`
- **Wake Mode**: `python NOVA/nova.py --wake`
- **Standard Voice Mode**: `python NOVA/nova.py`
- **Diagnostic Test Mode**: `python NOVA/nova.py --test`

## 🔒 Safety & Privacy
- **Confirmation Layer**: All desktop actions (typing, clicking, saving files) require explicit user approval.
- **Scrubbing**: Sensitive data like emails or tokens detected on screen are scrubbed before being sent to the AI.
- **Fail-safe**: Moving the mouse to any corner of the screen immediately halts any automation.

## 🛠 Project Structure
- `NOVA/ai/`: LLM client and intent classification.
- `NOVA/automation/`: OCR, screen capture, and desktop control.
- `NOVA/core/`: Routing, speech, safety, and runtime logic.
- `NOVA/features/`: System monitoring, apps, notes, and utilities.
- `NOVA/gui/`: PyQt5 interface and background workers.
- `NOVA/memory/`: SQLite database and preference management.
- `NOVA/skills/`: Integrated multi-step workflows.

## 📋 License
This project is for educational and personal use. Use responsibly.

---
*Developed by Rohitpvt & Antigravity AI*

## 🎤 Windows Microphone & Troubleshooting Guide

If NOVA displays *"I did not hear anything"* repeatedly or voice command detection fails, follow these steps to verify your microphone and system settings:

### 1. Windows System Checks
- **Microphone Access**: Go to **Settings** → **Privacy & security** → **Microphone**, and ensure that *Microphone access* and *Let apps access your microphone* are set to **On**.
- **Active Input Device**: Go to **Settings** → **System** → **Sound** → **Input**, and make sure your desired active microphone is selected as the default input device. Test the microphone bar to see if it registers voice volume.
- **Close Conflicting Apps**: Make sure other audio-heavy applications (Discord, Teams, Zoom, or recording tools) are not holding exclusive locks on your input device.

### 2. Run Diagnostics in NOVA Test Mode
NOVA provides dedicated diagnostic options to identify microphone issues:
```powershell
python NOVA/nova.py --test
```
- **Option `[31] List available microphones`**: Shows all detected audio device indexes and names. Use this to find the index of your physical microphone.
- **Option `[32] Test selected microphone with longer timeout`**: Prompts you to input your desired device index and timeout threshold to test audio capture and Google Speech recognition.
- **Option `[28] Test voice recognition once`**: Verifies capturing a standard command with default thresholds.

### 3. Customize Settings in `.env`
If you need to target a specific microphone device or fine-tune listening sensitivity, add these configurations to your `.env` file:
```env
# Index of the physical microphone to use (from Option 31, leave blank for system default)
NOVA_MIC_DEVICE_INDEX=
# Speech energy trigger threshold (Default: 300, increase if in a noisy environment)
NOVA_MIC_ENERGY_THRESHOLD=300
# Automatic background noise adaptation
NOVA_MIC_DYNAMIC_ENERGY_THRESHOLD=true
# Pause duration threshold after speech completes (Default: 0.8 seconds)
NOVA_MIC_PAUSE_THRESHOLD=0.8
# Max seconds to wait for starting speech
NOVA_MIC_LISTEN_TIMEOUT_SECONDS=8
# Max duration allowed for a single spoken phrase
NOVA_MIC_PHRASE_TIME_LIMIT_SECONDS=12
# Background noise calibration time
NOVA_MIC_AMBIENT_NOISE_DURATION=1.0
```

### 4. PyAudio & Python Version Compatibility Setup

Choosing the correct Python version and setup flow guarantees smooth voice commands without compilation headaches:

#### 📋 Recommended Python Versions
*   **Python 3.11 or 3.12 (Recommended / Easiest)**: Pre-compiled official binary wheels for PyAudio are readily available on PyPI. Setup is as simple as `pip install pyaudio`.
*   **Python 3.14+ (Requires Workaround)**: Official wheels are not yet available on PyPI for newer pre-releases/releases. Standard `pip install pyaudio` will attempt to compile from source and fail on Windows unless full C++ Visual Studio Build Tools are installed. Use the **PyAudioWPatch workaround** detailed below.

---

#### 🟢 Standard Setup (Python 3.11 / 3.12)
If you are running a supported Python version, execute:
```powershell
pip install pyaudio
```
If you encounter errors, try installing via `pipwin` to automatically fetch pre-compiled binaries:
```powershell
pip install pipwin
pipwin install pyaudio
```
Verify the installation by running:
```powershell
python -c "import pyaudio; print('PyAudio OK')"
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

---

#### 🟡 Advanced Python 3.14+ Workaround (PyAudioWPatch)
If you are on Python 3.14+ and standard installation fails, you can leverage `PyAudioWPatch` (a compiled community fork containing WASAPI loopback support and Python 3.14 wheels):

1.  **Install the library**:
    ```powershell
    pip install PyAudioWPatch
    ```
2.  **Verify the base import**:
    ```powershell
    python -c "import pyaudiowpatch; print('PyAudioWPatch OK')"
    ```
3.  **Create local compatibility shim**:
    Because the `speech_recognition` library strictly expects `import pyaudio`, you must create a local redirect package in your active virtual environment.
    *   Create a folder named `pyaudio` inside `venv\Lib\site-packages\pyaudio\`
    *   Create an `__init__.py` file in that folder containing:
        ```python
        from pyaudiowpatch import *
        from pyaudiowpatch import __version__
        ```
    *   *Warning: This compatibility shim is local to your environment. Do not commit virtual environment files (`venv/`) or site-packages folders to version control.*
4.  **Confirm the shim redirect works**:
    ```powershell
    python -c "import pyaudio; print('Shim Import OK:', pyaudio.__file__)"
    ```

---

### 5. Windows Microphone Permissions Checklist
If NOVA reports that the microphone is unavailable, check the following manual settings:
1.  **Microphone Privacy Access**:
    - Go to **Windows Settings** → **Privacy & security** → **Microphone**.
    - Ensure **Microphone access** is turned **On**.
    - Ensure **Let desktop apps access your microphone** is turned **On** (this allows Python and compiled EXEs to listen).
2.  **Active Device & Level Verification**:
    - Go to **Windows Settings** → **System** → **Sound** → **Input**.
    - Verify that your physical microphone is selected as the default input device.
    - Check the **Input volume meter** to see if it moves when you speak.
3.  **Device Conflicts**:
    - Close other audio-intensive applications (Discord, Teams, Zoom, screen recorders) that may be holding exclusive WASAPI/MME locks on your microphone.
    - Restart your terminal or PyQt5 GUI after altering Windows sound configurations.


