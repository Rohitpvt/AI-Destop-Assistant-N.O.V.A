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

### 4. PyAudio Troubleshooting
If Option `[31]` reports that PyAudio is missing, install it manually:
- **Windows**: Use `pip install pyaudio`. If you face compilation errors, install the precompiled binary wheel using:
  ```powershell
  pip install pipwin
  pipwin install pyaudio
  ```
  *(Or download the compatible `.whl` file matching your Python version from official mirrors and install it via `pip install <filename>.whl`).*

