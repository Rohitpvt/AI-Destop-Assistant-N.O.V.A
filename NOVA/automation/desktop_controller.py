import pyautogui
import pyperclip
from core.desktop_controller import *

# Maintain full backwards compatibility for old automation imports
def type_text(text: str, test_mode_active=True, takecommand_func=None) -> dict:
    """Wraps typing text using core desktop_controller bypass approval if configured."""
    return type_text(text, bypass_approval=True)

def paste_text(text: str, test_mode_active=True, takecommand_func=None) -> dict:
    """Wraps pasting text using core desktop_controller bypass approval."""
    try:
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def press_hotkey(keys: list[str], test_mode_active=True, takecommand_func=None) -> dict:
    """Wraps hotkeys using core desktop_controller bypass approval."""
    try:
        pyautogui.hotkey(*keys)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def move_mouse_relative(dx: int, dy: int, test_mode_active=True, takecommand_func=None) -> dict:
    """Moves mouse relatively."""
    try:
        pyautogui.moveRel(dx, dy)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def click_current_position(test_mode_active=True, takecommand_func=None) -> dict:
    """Clicks current mouse coordinates."""
    try:
        pyautogui.click()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def copy_clipboard() -> dict:
    """Copies current selection to clipboard."""
    try:
        pyautogui.hotkey('ctrl', 'c')
        text = pyperclip.paste()
        return {"success": True, "text": text}
    except Exception as e:
        return {"success": False, "error": str(e)}
