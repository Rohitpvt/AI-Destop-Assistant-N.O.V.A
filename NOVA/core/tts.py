import pyttsx3
import sys
import os
import threading
import logging
from contextlib import contextmanager

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        DEFAULT_NAME = "NOVA"
        VOICE_OUTPUT_ENABLED = True

_engine_lock = threading.Lock()

# Thread-local storage for engine and speech suppression state
_tts_thread_local = threading.local()

# Global tracking of last error and pyttsx3 import status
LAST_TTS_ERROR = None

def get_last_tts_error():
    global LAST_TTS_ERROR
    return LAST_TTS_ERROR

def get_active_voice_info():
    """Retrieves active voice ID and Name from thread-local engine if possible."""
    try:
        engine = _init_engine()
        if engine:
            voice_id = engine.getProperty('voice')
            voices = engine.getProperty('voices')
            for v in voices:
                if v.id == voice_id:
                    return {"id": v.id, "name": v.name}
            return {"id": voice_id, "name": "Unknown"}
    except Exception:
        pass
    return {"id": "None", "name": "None"}

def _init_engine():
    """Initializes the pyttsx3 engine in a thread-safe, thread-local manner."""
    global LAST_TTS_ERROR
    if not hasattr(_tts_thread_local, 'engine'):
        try:
            # SAPI5 requires COM initialization on Windows
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except ImportError:
                pass
            except Exception as ex:
                logging.warning(f"CoInitialize error: {ex}")

            new_engine = pyttsx3.init()
            voices = new_engine.getProperty('voices')
            if voices:
                new_engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
            new_engine.setProperty('rate', 170)
            new_engine.setProperty('volume', 1.0)
            _tts_thread_local.engine = new_engine
        except Exception as e:
            LAST_TTS_ERROR = str(e)
            logging.error(f"TTS Engine Initialization Failed on thread {threading.current_thread().name}: {e}")
            _tts_thread_local.engine = None
    return _tts_thread_local.engine

def suppress_speaking(suppress: bool = True):
    """Sets speech suppression state for the current thread."""
    _tts_thread_local._suppress_speak = suppress

def is_speaking_suppressed() -> bool:
    """Gets speech suppression state for the current thread."""
    return getattr(_tts_thread_local, '_suppress_speak', False)

@contextmanager
def speech_suppressed():
    """Context manager to suppress speech within a block, always restoring the initial state."""
    old_state = is_speaking_suppressed()
    suppress_speaking(True)
    try:
        yield
    finally:
        suppress_speaking(old_state)

def speak(audio) -> None:
    """Converts text to speech using pyttsx3 with thread-local safety."""
    if not audio:
        return

    # Print to console as usual
    print(f"[{config.DEFAULT_NAME}]: {audio}")
    sys.stdout.flush()

    # Skip actual audio output if speech is suppressed on this thread
    if is_speaking_suppressed():
        return

    # Skip actual audio output if voice output is globally disabled in config
    if hasattr(config, 'VOICE_OUTPUT_ENABLED') and not config.VOICE_OUTPUT_ENABLED:
        return

    global LAST_TTS_ERROR
    with _engine_lock:
        try:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except ImportError:
                pass
            except Exception as ex:
                pass
            
            engine = _init_engine()
            if engine:
                engine.say(str(audio))
                engine.runAndWait()
            else:
                logging.warning("TTS Engine not available on this thread. Response printed only.")
        except Exception as e:
            LAST_TTS_ERROR = str(e)
            logging.error(f"Error during TTS execution on thread {threading.current_thread().name}: {e}")
            # Reset thread-local engine for retry next time
            if hasattr(_tts_thread_local, 'engine'):
                del _tts_thread_local.engine

def speak_response(response_text: str) -> None:
    """Central bridge for final user-facing responses to be spoken aloud exactly once."""
    if not response_text:
        return

    # Skip actual audio output if voice output is globally disabled in config
    if hasattr(config, 'VOICE_OUTPUT_ENABLED') and not config.VOICE_OUTPUT_ENABLED:
        return

    # Skip logs or generic developer status responses
    log_keywords = [
        "command executed successfully",
        "told the time",
        "told the date",
        "went offline",
        "going offline",
        "shutdown cancelled",
        "no matching keyword found"
    ]
    resp_lower = response_text.lower().strip()
    if any(kw in resp_lower for kw in log_keywords):
        return

    # Speak response directly, ensuring suppress_speaking is temporarily False for final speech output
    try:
        old_suppress = is_speaking_suppressed()
        suppress_speaking(False)
        speak(response_text)
        suppress_speaking(old_suppress)
    except Exception as e:
        global LAST_TTS_ERROR
        LAST_TTS_ERROR = str(e)
        logging.error(f"Failed to speak response: {e}")
