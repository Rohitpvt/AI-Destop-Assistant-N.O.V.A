import os
import sys

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        REQUIRE_CONFIRMATION_FOR_ACTIONS = True
        VOICE_CONFIRMATION_ENABLED = True

from core.tts import speak
from core.logger import log_info

# Optional callback for GUI confirmation
_gui_confirmation_callback = None

def register_gui_confirmation_callback(callback):
    """Allows the GUI to register a function to handle confirmation dialogs."""
    global _gui_confirmation_callback
    _gui_confirmation_callback = callback

def confirm_action(action_description: str, test_mode_active=True, takecommand_func=None) -> bool:
    """Asks the user for explicit confirmation before performing a desktop action."""
    if not config.REQUIRE_CONFIRMATION_FOR_ACTIONS:
        return True

    # Step 1: Try GUI confirmation if registered
    if _gui_confirmation_callback:
        log_info(f"Requesting GUI confirmation for: {action_description}")
        return _gui_confirmation_callback(action_description)

    # Step 2: Fallback to Terminal/Voice
    msg = f"NOVA wants to: {action_description}. Should I proceed?"
    speak(msg)
    print(f"\n[CONFIRMATION REQUIRED]: {msg} (yes/no)")
    
    ans = ""
    # Try voice confirmation first if enabled and in voice mode (not test mode)
    if not test_mode_active and config.VOICE_CONFIRMATION_ENABLED and takecommand_func:
        ans = takecommand_func().lower().strip()
        if not ans:
            speak("I didn't catch that. Please type your response.")
            ans = input("Enter yes to confirm or any other key to cancel: ").lower().strip()
    elif test_mode_active:
        ans = input("Your response: ").lower().strip()
    elif takecommand_func:
        ans = takecommand_func().lower().strip()
    else:
        ans = "no"

    if ans in ["yes", "y", "allow", "proceed", "confirm", "okay", "sure"]:
        log_info(f"Action Approved: {action_description}")
        return True
    else:
        log_info(f"Action Denied: {action_description}")
        speak("Action cancelled.")
        return False
