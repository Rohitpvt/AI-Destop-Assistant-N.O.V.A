import os
import datetime
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        NOTES_DIR = os.getcwd()

from core.tts import speak
from core.logger import log_event

def take_note(note_text):
    """Takes a note and saves it to a file."""
    if note_text:
        try:
            note_file = os.path.join(config.NOTES_DIR, "notes.txt")
            with open(note_file, "a") as f:
                f.write(f"{datetime.datetime.now()}: {note_text}\n")
            speak("Note saved.")
            log_event("take note", "Note", "Success")
        except Exception as e:
            speak(f"Failed to save note: {e}")
            log_event("take note", "Note", "Failure", str(e))
