# Testing Guide - NOVA Desktop Voice Assistant

This guide provides instructions on how to set up, run, and test the NOVA project safely using the newly implemented test mode.

## 1. Installation

### Prerequisites
- Python 3.13+ (Works on older versions too, but fixes are included for newer versions).
- [Optional] Microphone and Speakers for Voice Mode.

### Steps
1. **Activate Virtual Environment**:
   ```powershell
   .\venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
   *Note: If PyAudio fails on Windows, see the notes in `requirements.txt` for workaround links.*

## 2. Running NOVA

### Normal Voice Mode
To run NOVA with full voice support:
```powershell
python NOVA/nova.py
```

### Test Mode (Recommended for Verification)
To run NOVA in a terminal-based test mode without needing a microphone:
```powershell
python NOVA/nova.py --test
```

## 3. Feature Test Checklist

In **Test Mode**, you can verify each feature using the menu or by typing commands manually.

| Feature | Menu Option | Manual Command Example | Expected Result |
| :--- | :---: | :--- | :--- |
| **Greeting** | [1] | `wish me` | NOVA greets you based on time. |
| **Time/Date** | [2] | `what is the time` | Current time/date is printed/spoken. |
| **Websites** | [3] | `open youtube` | Browser opens the specified site. |
| **Google Search** | [4] | `search google for cats` | Browser performs a Google search. |
| **Wikipedia** | [5] | `wikipedia Elon Musk` | Summary is displayed in terminal. |
| **Music** | [7] | `play music` | A random audio file from Music folder plays. |
| **Screenshots** | [9] | `take screenshot` | A screenshot is saved to project root. |
| **Jokes** | [10] | `tell me a joke` | A random joke is printed. |

### Manual Command Mode
In Test Mode, you can enter **Manual Command Mode** by typing `m`. This allows you to type any natural command (e.g., `open youtube`, `search google for python`, `time`, `exit`) and see how NOVA processes it.

## 4. Common Errors & Fixes

| Error | Cause | Fix |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'aifc'` | Python 3.13+ removal | Already fixed via `standard-aifc` in `requirements.txt`. |
| `FileNotFoundError: Pictures` | Missing system folder | Already fixed; screenshots now save to project root. |
| `PyAudio` installation failed | Missing Build Tools | Use the pre-compiled `.whl` files mentioned in `requirements.txt`. |
| No sound output | No audio device | NOVA will fall back to printing responses in the terminal. |

## 5. Configuration
You can customize settings (Name, Log Level, Paths) in `.env` or directly in `NOVA/config.py`. 

### Log Location
- Logs are stored in: `logs/nova.log`
- Rotating logs are enabled (keeps last 3 backups).

### Safe Automation
- All desktop actions (typing, clicking, etc.) require explicit user confirmation.
- PyAutoGUI Fail-safe is active: Move the mouse to any corner of the screen to abort.

### Screen Awareness
- Tesseract OCR is required for screen reading.
- Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- In .env, set: `NOVA_TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`

### Memory Storage
- Interaction history and preferences are stored in: `data/nova_memory.db`
- You can manage memory using commands like `show memory` and `clear memory`.

### Data Location
- Assistant identity and persistent data are stored in: `data/`
