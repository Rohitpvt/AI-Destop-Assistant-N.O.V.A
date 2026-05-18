import time
from core import session_context, desktop_controller
from core.tts import speak

def is_action_allowed(action_dict: dict) -> bool:
    """Verifies that the staged action is not destructive or malicious."""
    action_type = action_dict.get("action")
    target = action_dict.get("target", "")
    args = action_dict.get("arguments", {})
    
    # Destructive terms block
    target_lower = str(target).lower()
    destructive_keywords = ["shutdown", "restart", "format", "destroy", "delete file", "rmdir", "del ", "erase"]
    
    for kw in destructive_keywords:
        if kw in target_lower:
            return False
            
    text = str(args.get("text", "")).lower()
    for kw in destructive_keywords:
        if kw in text:
            return False
            
    keys = args.get("keys", [])
    keys_lower = [str(k).lower() for k in keys]
    if "alt" in keys_lower and "f4" in keys_lower:
        return False
        
    key = str(args.get("key", "")).lower()
    if "delete" in key or "shutdown" in key:
        return False
            
    return True

def request_approval(action_dict: dict) -> str:
    """Stages the pending action in context and returns the confirmation prompt."""
    session_context.set_pending_approval(action_dict)
    
    action_type = action_dict.get("action")
    target = action_dict.get("target", "")
    args = action_dict.get("arguments", {})
    
    if action_type == "click":
        if target:
            prompt = f"I'm ready to click the {target} button. Say 'confirm' to continue or 'cancel' to stop."
        else:
            x = args.get("x")
            y = args.get("y")
            prompt = f"I'm ready to click at coordinates ({x}, {y}). Say 'confirm' to continue or 'cancel' to stop."
    elif action_type == "type":
        text = args.get("text", "")
        prompt = f"I'm ready to type '{text}' into the active application. Say 'confirm' to continue or 'cancel' to stop."
    elif action_type == "press_key":
        key = args.get("key", "")
        prompt = f"I'm ready to press the '{key}' key. Say 'confirm' to continue or 'cancel' to stop."
    elif action_type == "hotkey":
        keys = args.get("keys", [])
        prompt = f"I'm ready to press the hotkey '{'+'.join(keys)}'. Say 'confirm' to continue or 'cancel' to stop."
    elif action_type == "scroll":
        amount = args.get("amount", 0)
        prompt = f"I'm ready to scroll by {amount}. Say 'confirm' to continue or 'cancel' to stop."
    else:
        prompt = "I have a pending action requiring your approval. Say 'confirm' to continue or 'cancel' to stop."
        
    speak(prompt)
    return prompt

def execute_pending_action() -> dict:
    """Validates parameters, window integrity, and executes the staged pending action."""
    context = session_context.get_context()
    pending = context.get("pending_approval")
    
    if not pending:
        return {"success": False, "error": "No pending action found."}
        
    # Validation 1: Expiry
    elapsed = time.time() - pending["created_at"]
    if elapsed > pending["expires_after_seconds"]:
        session_context.clear_pending_approval()
        err_msg = "Approval expired."
        speak(err_msg)
        return {"success": False, "error": err_msg}
        
    # Validation 2: Active Window mismatch check
    current_title = desktop_controller.get_active_window_title()
    if current_title != pending["active_window_title"]:
        session_context.clear_pending_approval()
        err_msg = "Active window has changed unexpectedly."
        speak(err_msg)
        return {"success": False, "error": err_msg}
        
    # Validation 3: Safety check
    if not is_action_allowed(pending):
        session_context.clear_pending_approval()
        err_msg = "Action blocked: Destructive command detected."
        speak(err_msg)
        return {"success": False, "error": err_msg}
        
    # Execution
    action_type = pending.get("action")
    args = pending.get("arguments", {})
    res = {"success": False, "error": "Unknown action."}
    
    try:
        if action_type == "click":
            res = desktop_controller.click_at(args["x"], args["y"], bypass_approval=True)
        elif action_type == "type":
            res = desktop_controller.type_text(args["text"], bypass_approval=True)
        elif action_type == "press_key":
            res = desktop_controller.press_key(args["key"], bypass_approval=True)
        elif action_type == "hotkey":
            res = desktop_controller.hotkey(*args["keys"], bypass_approval=True)
        elif action_type == "scroll":
            res = desktop_controller.scroll(args["amount"], bypass_approval=True)
    except Exception as e:
        res = {"success": False, "error": str(e)}
        
    session_context.clear_pending_approval()
    
    if res["success"]:
        msg = "Action executed successfully."
        speak(msg)
        return {"success": True, "message": msg}
    else:
        err_msg = f"Execution failed: {res.get('error')}"
        speak(err_msg)
        return {"success": False, "error": err_msg}

def cancel_pending_action() -> str:
    """Aborts the pending action cleanly."""
    session_context.clear_pending_approval()
    msg = "Cancelled."
    speak(msg)
    return msg
