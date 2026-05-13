import speech_recognition as sr
import os
import sys
import logging

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        LISTEN_TIMEOUT_SECONDS = 5
        PHRASE_TIME_LIMIT_SECONDS = 10

from core.logger import log_info, log_event

def takecommand(force_text=False) -> str:
    """Listens for a command from the microphone and returns it as text."""
    if force_text:
        return input("Enter command: ").lower().strip()

    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 1
            audio = r.listen(source, 
                             timeout=config.LISTEN_TIMEOUT_SECONDS, 
                             phrase_time_limit=config.PHRASE_TIME_LIMIT_SECONDS)
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return ""
    except Exception as e:
        log_event("takecommand", "Speech", "Failure", f"Microphone error: {str(e)}")
        print(f"Microphone error: {e}")
        return ""

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        return query.lower().strip()
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        log_event("takecommand", "Speech", "Failure", f"Recognition error: {str(e)}")
        print(f"Recognition error: {e}")
        return ""
