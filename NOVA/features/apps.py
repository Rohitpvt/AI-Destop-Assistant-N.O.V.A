import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        APP_PATHS = {}

from core.tts import speak
from core.logger import log_event

def open_app(app_name):
    """Opens an application based on config mapping."""
    app_path = config.APP_PATHS.get(app_name.lower())
    if app_path:
        try:
            os.startfile(app_path)
            speak(f"Opening {app_name}")
            log_event(f"open {app_name}", "Open App", "Success")
        except Exception as e:
            speak(f"Failed to open {app_name}: {e}")
            log_event(f"open {app_name}", "Open App", "Failure", str(e))
    else:
        speak(f"Application {app_name} is not configured in APP_PATHS.")
        log_event(f"open {app_name}", "Open App", "Failure", "Not configured")
