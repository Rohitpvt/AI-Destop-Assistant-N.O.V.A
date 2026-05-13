# NOVA Release Notes - v1.0.0-alpha

## Overview
NOVA (Next-generation Omniscient Virtual Assistant) is a modular, AI-powered desktop assistant designed for secure, context-aware automation and productivity.

## 🚀 Features
- **Intelligence**: Intent classification and chat via NVIDIA/OpenAI-compatible LLMs.
- **Vision**: OCR-based screen awareness to summarize and "see" your desktop.
- **Automation**: Safe, user-approved desktop interactions (typing, hotkeys, mouse).
- **Memory**: Persistent SQLite storage for user preferences and interaction history.
- **Monitoring**: Real-time system resource reporting (CPU, RAM, Battery, Windows).
- **Integrated Skills**: Multi-step workflows like Screen-to-Note and Session Summarization.

## 🛠 Supported Modes
1. **GUI Mode**: `python NOVA/nova.py --gui` - Modern PyQt5 dashboard.
2. **Wake Mode**: `python NOVA/nova.py --wake` - Hands-free "Hey NOVA" listening.
3. **Voice Mode**: `python NOVA/nova.py` - Standard continuous voice interaction.
4. **Test Mode**: `python NOVA/nova.py --test` - Terminal-based diagnostic suite.

## 🔒 Safety & Privacy
- **Human-in-the-Loop**: All desktop automation and data-saving tasks require explicit user confirmation.
- **Local First**: Memory and logs are stored locally.
- **Data Scrubbing**: OCR text is scrubbed of sensitive PII (emails, tokens) before processing.
- **Fail-safe**: Slapping the mouse into any screen corner aborts all automation.

## 📋 Requirements
- Python 3.8+
- Tesseract OCR (Optional, for screen reading)
- NVIDIA API Key (Optional, for LLM brain)
- Active Internet (For speech recognition and LLM)

## ⚠️ Known Limitations
- OCR accuracy depends on screen resolution and font clarity.
- Wake mode performance varies based on microphone quality and background noise.
- Single monitor support only for screen capture.

## 🗺 Future Roadmap
- [ ] Packaging as a standalone Windows executable (.exe).
- [ ] Multi-monitor support for vision.
- [ ] Advanced browser automation via secure extensions.
- [ ] Plugin/Skill marketplace architecture.
- [ ] Enhanced GUI animations and "Iron Man" style HUD.

---
*Developed by Rohitpvt & Antigravity AI*
