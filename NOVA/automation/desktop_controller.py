import pyautogui
import pyperclip
import os
import sys

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        AUTOMATION_ENABLED = True
        PYAUTOGUI_FAILSAFE = True
        AUTOMATION_PAUSE_SECONDS = 0.2

from core.safety import confirm_action
from core.logger import log_info, log_event

# Initialize PyAutoGUI settings
pyautogui.FAILSAFE = config.PYAUTOGUI_FAILSAFE
pyautogui.PAUSE = config.AUTOMATION_PAUSE_SECONDS

def type_text(text: str, test_mode_active=True, takecommand_func=None) -> dict:
    """Types the given text after user confirmation."""
    if not config.AUTOMATION_ENABLED:
        return {"success": False, "error": "Automation is disabled."}

    if confirm_action(f"type '{text}'", test_mode_active, takecommand_func):
        try:
            pyautogui.write(text)
            return {"success": True}
        except Exception as e:
            log_event("type_text", "Desktop Controller", "Failure", str(e))
            return {"success": False, "error": str(e)}
    return {"success": False, "error": "User denied action."}

def paste_text(text: str, test_mode_active=True, takecommand_func=None) -> dict:
    """Pastes the given text using clipboard after user confirmation."""
    if not config.AUTOMATION_ENABLED:
        return {"success": False, "error": "Automation is disabled."}

    if confirm_action(f"paste '{text}'", test_mode_active, takecommand_func):
        try:
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            return {"success": True}
        except Exception as e:
            log_event("paste_text", "Desktop Controller", "Failure", str(e))
            return {"success": False, "error": str(e)}
    return {"success": False, "error": "User denied action."}

def press_hotkey(keys: list[str], test_mode_active=True, takecommand_func=None) -> dict:
    """Presses a combination of keys after user confirmation."""
    if not config.AUTOMATION_ENABLED:
        return {"success": False, "error": "Automation is disabled."}

    # Safe whitelist
    allowed_hotkeys = [
        ['ctrl', 'c'], ['ctrl', 'v'], ['ctrl', 'a'], ['ctrl', 's'],
        ['alt', 'tab'], ['esc'], ['enter']
    ]
    
    if keys not in allowed_hotkeys:
        return {"success": False, "error": f"Hotkey {keys} is not in the safe whitelist."}

    if confirm_action(f"press keys {'+'.join(keys)}", test_mode_active, takecommand_func):
        try:
            pyautogui.hotkey(*keys)
            return {"success": True}
        except Exception as e:
            log_event("press_hotkey", "Desktop Controller", "Failure", str(e))
            return {"success": False, "error": str(e)}
    return {"success": False, "error": "User denied action."}

def move_mouse_relative(dx: int, dy: int, test_mode_active=True, takecommand_func=None) -> dict:
    """Moves the mouse relative to current position after confirmation."""
    if not config.AUTOMATION_ENABLED:
        return {"success": False, "error": "Automation is disabled."}

    if confirm_action(f"move mouse by ({dx}, {dy})", test_mode_active, takecommand_func):
        try:
            pyautogui.moveRel(dx, dy)
            return {"success": True}
        except Exception as e:
            log_event("move_mouse", "Desktop Controller", "Failure", str(e))
            return {"success": False, "error": str(e)}
    return {"success": False, "error": "User denied action."}

def click_current_position(test_mode_active=True, takecommand_func=None) -> dict:
    """Clicks at the current mouse position after confirmation."""
    if not config.AUTOMATION_ENABLED:
        return {"success": False, "error": "Automation is disabled."}

    if confirm_action("click the current position", test_mode_active, takecommand_func):
        try:
            pyautogui.click()
            return {"success": True}
        except Exception as e:
            log_event("click", "Desktop Controller", "Failure", str(e))
            return {"success": False, "error": str(e)}
    return {"success": False, "error": "User denied action."}

def copy_clipboard() -> dict:
    """Copies current selection to clipboard (does not require confirmation for safety)."""
    try:
        pyautogui.hotkey('ctrl', 'c')
        text = pyperclip.paste()
        return {"success": True, "text": text}
    except Exception as e:
        return {"success": False, "error": str(e)}
