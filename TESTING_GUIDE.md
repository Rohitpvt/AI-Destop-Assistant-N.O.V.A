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

### Modern Desktop GUI
- Start with: `python NOVA\nova.py --gui`
- Chat interface with live logs and memory.
- Integrated voice and wake mode buttons.
- Visual confirmation dialogs for safe automation.

### Voice Wake Mode
- Start with: `python NOVA\nova.py --wake`
- Wake words: 'nova', 'hey nova'.
- Sleep command: 'sleep' or 'go to sleep'.
- Exit command: 'exit' or 'shutdown nova'.

### Advanced Skills
- Combined routines: Screen-to-note, Memory-to-note.
- All data-saving skills require confirmation.

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
- Assistant identity and persistent data are stored in: data/

## 6. Voice Command & Microphone Diagnostics

If you are testing speech recognition or always-listening wake mode, utilize the following steps to ensure perfect operation across Python versions:

### 📋 Recommended Python Version & Setup
- **Python 3.11 / 3.12 (Easiest)**: Precompiled PyAudio binary wheels are readily available. Run `pip install pyaudio`.
- **Python 3.14+ (Requires Workaround)**: Precompiled wheels are not uploaded to PyPI yet. Install `PyAudioWPatch` (community fork) and shim it locally:
  ```powershell
  pip install PyAudioWPatch
  ```
  Create a folder `pyaudio` under `venv\Lib\site-packages\pyaudio\` and create an `__init__.py` in it with:
  ```python
  from pyaudiowpatch import *
  from pyaudiowpatch import __version__
  ```
  This shims `import pyaudio` successfully for speech libraries without committing any local env files!

---

### 🎙️ Diagnostic CLI Commands
Start NOVA in test mode:
```powershell
python NOVA/nova.py --test
```
1.  **Option `[31] List available microphones`**:
    - Queries the local host API for all physical/virtual input audio devices.
    - Displays their PyAudio device indexes and names.
2.  **Option `[32] Test selected microphone with longer timeout`**:
    - Lets you choose a custom microphone index.
    - Calibrates background noise dynamically.
    - Listens for a phrase with a configurable timeout (e.g. 15s) and prints a structured response.
3.  **Option `[28] Test voice recognition once`**:
    - Listens for a standard phrase with the default 8s timeout and prints success/error metrics.
4.  **Option `[29] Test voice output (TTS)`**:
    - Plays a test spoken audio signal to verify standard text-to-speech engine outputs.

---

### ⚙️ Adjusting Sensitivity in `.env`
If you notice that speech detection is timing out or is too sensitive:
```env
# Specific physical device index from Option 31 (leave empty for Windows Sound Mapper)
NOVA_MIC_DEVICE_INDEX=
# Speech energy trigger threshold (Default: 300, increase to 500-1000 in noisy rooms)
NOVA_MIC_ENERGY_THRESHOLD=300
# Automatic background noise adaptation (true/false)
NOVA_MIC_DYNAMIC_ENERGY_THRESHOLD=true
# Pause duration threshold after speech completes (Default: 0.8 seconds)
NOVA_MIC_PAUSE_THRESHOLD=0.8
# Max seconds to wait for starting speech (Default: 8)
NOVA_MIC_LISTEN_TIMEOUT_SECONDS=8
# Max duration allowed for a single spoken phrase (Default: 12)
NOVA_MIC_PHRASE_TIME_LIMIT_SECONDS=12
# Background noise calibration time (Default: 1.0)
NOVA_MIC_AMBIENT_NOISE_DURATION=1.0
```

---

### 🔒 Windows Microphone Permission Checklist
- **Microphone Access**: Settings → Privacy & security → Microphone → Ensure *Microphone access* and *Let desktop apps access your microphone* are set to **On**.
- **System Sound Input**: Settings → System → Sound → Input → Verify that your physical microphone is selected as the default input device, and that the volume meter moves when you speak.
- **Resource Locking**: Close other audio-intensive applications (Discord, Teams, Zoom, screen recorders) that may be holding exclusive locks.
- **Restart requirement**: Restart the terminal or PyQt5 GUI app after modifying system sound configurations.

---

### 🔍 Advanced Voice Troubleshooting Table

| Problem | Possible Causes | Fix |
| :--- | :--- | :--- |
| **"Microphone is unavailable. Check Windows input settings."** | 1. PyAudio dependency missing.<br>2. Incorrect Python version (3.14+ lacks PyAudio wheel).<br>3. Windows microphone privacy setting blocked.<br>4. Packaged standalone EXE missing bundled audio binaries. | 1. Run Option `[31]` to check for errors.<br>2. Install `pyaudio` (on 3.11/3.12) or install `PyAudioWPatch` and shim it locally (on 3.14+).<br>3. Enable microphone privacy permissions for desktop apps.<br>4. Recompile with `python build_nova.py` (which includes explicit `--hidden-import pyaudiowpatch` support). |
| **"I did not hear anything. Please speak closer." (Repeated Silences)** | 1. Microphone volume set too soft.<br>2. Wrong active microphone selected.<br>3. Listening timeout too short.<br>4. Adapting to noisy background room calibration. | 1. Run Option `[32]` with index `0` or custom mic index to test live capture.<br>2. Set `NOVA_MIC_DEVICE_INDEX` in `.env` to pin a specific active device.<br>3. Increase `NOVA_MIC_LISTEN_TIMEOUT_SECONDS` to `15` in `.env`.<br>4. Increase `NOVA_MIC_ENERGY_THRESHOLD` to prevent background noise from freezing the detector. |


