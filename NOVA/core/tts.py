import pyttsx3
import sys
import os
import threading
import logging

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        DEFAULT_NAME = "NOVA"

_engine_lock = threading.Lock()
_engine = None

def _init_engine():
    """Initializes the pyttsx3 engine in a thread-safe manner."""
    global _engine
    if _engine is None:
        try:
            # On Windows, pyttsx3 uses SAPI5 which requires a COM context.
            # Lazy initialization inside the calling thread often helps.
            new_engine = pyttsx3.init()
            voices = new_engine.getProperty('voices')
            if voices:
                new_engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
            new_engine.setProperty('rate', 170)
            new_engine.setProperty('volume', 1.0)
            _engine = new_engine
        except Exception as e:
            logging.error(f"TTS Engine Initialization Failed: {e}")
            _engine = None
    return _engine

def speak(audio) -> None:
    """Converts text to speech using pyttsx3 with thread safety."""
    if not audio:
        return

    print(f"[{config.DEFAULT_NAME}]: {audio}")
    sys.stdout.flush()

    # Thread-safe speaking
    with _engine_lock:
        engine = _init_engine()
        if engine:
            try:
                # Some drivers (SAPI5) can hang if not handled carefully in threads
                engine.say(str(audio))
                engine.runAndWait()
            except Exception as e:
                logging.error(f"Error during TTS execution: {e}")
                # Try to re-init next time
                global _engine
                _engine = None
        else:
            logging.warning("TTS Engine not available. Response printed only.")
