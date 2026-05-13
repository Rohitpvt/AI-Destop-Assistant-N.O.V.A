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
