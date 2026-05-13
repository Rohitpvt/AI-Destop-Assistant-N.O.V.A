import os
import sys

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        REQUIRE_CONFIRMATION_FOR_ACTIONS = True

from core.tts import speak
from core.logger import log_info

def confirm_action(action_description: str, test_mode_active=True, takecommand_func=None) -> bool:
    """Asks the user for explicit confirmation before performing a desktop action."""
    if not config.REQUIRE_CONFIRMATION_FOR_ACTIONS:
        return True

    msg = f"NOVA wants to: {action_description}. Should I proceed?"
    speak(msg)
    print(f"\n[CONFIRMATION REQUIRED]: {msg} (yes/no)")
    
    if test_mode_active:
        ans = input("Your response: ").lower().strip()
    elif takecommand_func:
        ans = takecommand_func().lower().strip()
    else:
        # Fallback if no input method is provided
        ans = "no"

    if ans in ["yes", "y", "allow", "proceed"]:
        log_info(f"Action Approved: {action_description}")
        return True
    else:
        log_info(f"Action Denied: {action_description}")
        speak("Action cancelled.")
        return False
