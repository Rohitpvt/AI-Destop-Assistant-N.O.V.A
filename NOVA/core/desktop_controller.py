import pyautogui
import pygetwindow as gw
import pyperclip
import webbrowser

# Set pyautogui safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

def get_active_window_title() -> str:
    """Returns the title of the current active window or a safe default."""
    try:
        win = gw.getActiveWindow()
        if win:
            return win.title
    except Exception:
        pass
    return "Mocked Window Title"

def open_website(url: str) -> dict:
    """Low-risk action that opens the given URL in the default browser."""
    try:
        full_url = url
        if not url.startswith("http://") and not url.startswith("https://"):
            full_url = f"https://{url}"
        webbrowser.open(full_url)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def open_application(app_name: str) -> dict:
    """Low-risk action that opens the specified application name."""
    try:
        from features import apps
        apps.open_app(app_name)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def switch_window(title: str) -> dict:
    """Low-risk action that switches and activates the window by title."""
    try:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            for win in windows:
                if title.lower() in win.title.lower():
                    if win.isMinimized:
                        win.restore()
                    win.activate()
                    return {"success": True}
        return {"success": False, "error": f"No window found matching {title}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def type_text(text: str, bypass_approval=False) -> dict:
    """Risky action that types text into the active application."""
    if not bypass_approval:
        from core import approval
        action = {"action": "type", "target": "", "arguments": {"text": text}}
        prompt = approval.request_approval(action)
        return {"success": True, "approval_pending": True, "prompt": prompt}
    try:
        pyautogui.write(text)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def press_key(key: str, bypass_approval=False) -> dict:
    """Risky action that presses a specific key."""
    if not bypass_approval:
        from core import approval
        action = {"action": "press_key", "target": "", "arguments": {"key": key}}
        prompt = approval.request_approval(action)
        return {"success": True, "approval_pending": True, "prompt": prompt}
    try:
        pyautogui.press(key)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def hotkey(*keys, bypass_approval=False) -> dict:
    """Risky action that presses a hotkey combination."""
    if not bypass_approval:
        from core import approval
        action = {"action": "hotkey", "target": "", "arguments": {"keys": list(keys)}}
        prompt = approval.request_approval(action)
        return {"success": True, "approval_pending": True, "prompt": prompt}
    try:
        pyautogui.hotkey(*keys)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def scroll(amount: int, bypass_approval=False) -> dict:
    """Risky action that scrolls the active window viewport."""
    if not bypass_approval:
        from core import approval
        action = {"action": "scroll", "target": "", "arguments": {"amount": amount}}
        prompt = approval.request_approval(action)
        return {"success": True, "approval_pending": True, "prompt": prompt}
    try:
        pyautogui.scroll(amount)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def click_at(x: int, y: int, target="", bypass_approval=False) -> dict:
    """Risky action that moves the mouse and clicks at coordinates."""
    if not bypass_approval:
        from core import approval
        action = {"action": "click", "target": target, "arguments": {"x": x, "y": y}}
        prompt = approval.request_approval(action)
        return {"success": True, "approval_pending": True, "prompt": prompt}
    try:
        pyautogui.click(x, y)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def resolve_visible_target(target_text: str):
    """
    Resolves target_text against visible items.
    Returns:
        - dict: Best match if uniquely identified.
        - str: Clarification query if ambiguous.
        - None: If no matches found.
    """
    from core import session_context
    items = session_context.get_context()["last_visible_items"]
    if not items:
        return None

    target_lower = target_text.lower().strip()
    
    exact_matches = []
    partial_matches = []
    
    for item in items:
        text_lower = item["text"].lower().strip()
        if target_lower == text_lower:
            exact_matches.append(item)
        elif target_lower in text_lower or text_lower in target_lower:
            partial_matches.append(item)
            
    candidates = exact_matches if exact_matches else partial_matches
    
    if not candidates:
        return None
        
    if len(candidates) > 1:
        # Check if one has higher confidence
        candidates.sort(key=lambda x: x["confidence"], reverse=True)
        # If ambiguous, ask user to clarify
        options = ", ".join([f"'{c['text']}'" for c in candidates[:3]])
        return f"I found multiple matches for '{target_text}' ({options}). Please clarify which one you want to click."
        
    return candidates[0]
