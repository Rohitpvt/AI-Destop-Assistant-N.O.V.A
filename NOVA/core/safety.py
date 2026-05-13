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

def confirm_action(action_description: str, test_mode_active=True, takecommand_func=None) -> bool:
    """Asks the user for explicit confirmation before performing a desktop action."""
    if not config.REQUIRE_CONFIRMATION_FOR_ACTIONS:
        return True

    msg = f"NOVA wants to: {action_description}. Should I proceed?"
    speak(msg)
    print(f"\n[CONFIRMATION REQUIRED]: {msg} (yes/no)")
    
    ans = ""
    # Try voice confirmation first if enabled and in voice mode (not test mode)
    if not test_mode_active and config.VOICE_CONFIRMATION_ENABLED and takecommand_func:
        ans = takecommand_func().lower().strip()
        # If voice response is empty or unclear, fall back to typed if possible
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
