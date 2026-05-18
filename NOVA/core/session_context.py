import time

_context = {
    "active_app": "",
    "active_window_title": "Mocked Window Title",
    "active_website": "",
    "active_task": "",
    "last_screen_summary": "",
    "last_visible_items": [],
    "last_user_intent": "",
    "last_target": "",
    "last_action_plan": None,
    "pending_approval": None,
    "control_mode": "safe"
}

def update_context(**kwargs):
    """Dynamically updates tracked state context parameters."""
    global _context
    for k, v in kwargs.items():
        if k in _context:
            _context[k] = v

def get_context() -> dict:
    """Returns the current state context dictionary."""
    global _context
    return _context

def clear_context():
    """Resets context fields to their pristine safe configurations."""
    global _context
    _context.update({
        "active_app": "",
        "active_window_title": "Mocked Window Title",
        "active_website": "",
        "active_task": "",
        "last_screen_summary": "",
        "last_visible_items": [],
        "last_user_intent": "",
        "last_target": "",
        "last_action_plan": None,
        "pending_approval": None,
        "control_mode": "safe"
    })

def set_pending_approval(action: dict):
    """Stages a desktop control action requiring explicit approval."""
    global _context
    from core import desktop_controller
    
    _context["pending_approval"] = {
        "action": action.get("action"),
        "target": action.get("target"),
        "arguments": action.get("arguments", {}),
        "active_window_title": desktop_controller.get_active_window_title(),
        "created_at": time.time(),
        "expires_after_seconds": action.get("expires_after_seconds", 30)
    }

def clear_pending_approval():
    """Clears the currently staged pending action."""
    global _context
    _context["pending_approval"] = None

def has_pending_approval() -> bool:
    """Checks whether an action is currently pending confirmation."""
    global _context
    return _context["pending_approval"] is not None
