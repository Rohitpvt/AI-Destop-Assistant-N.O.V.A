import pyttsx3
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        DEFAULT_NAME = "NOVA"

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
except Exception as e:
    print(f"Warning: pyttsx3 initialization failed: {e}")
    engine = None

def speak(audio) -> None:
    """Converts text to speech using pyttsx3, or prints to terminal if TTS fails."""
    if engine:
        try:
            engine.say(audio)
            engine.runAndWait()
        except Exception as e:
            print(f"Error speaking: {e}")
            print(f"[{config.DEFAULT_NAME}]: {audio}")
            sys.stdout.flush()
    else:
        print(f"[{config.DEFAULT_NAME}]: {audio}")
        sys.stdout.flush()
