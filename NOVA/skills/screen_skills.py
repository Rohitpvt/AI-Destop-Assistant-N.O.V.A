import os
import sys
import datetime

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        NOTES_DIR = "notes"

from automation import screen_reader
from memory import memory_db
from core.safety import confirm_action
from core.logger import log_info, log_event

def summarize_screen_to_note(test_mode_active=True, takecommand_func=None) -> dict:
    """Captures, OCRs, summarizes screen and saves to a note."""
    res = screen_reader.get_screen_context()
    if not res["success"]:
        return res

    summary = res["summary"]
    
    # Confirm before saving
    if confirm_action("save a summary of your current screen to a note", test_mode_active, takecommand_func):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"screen_summary_{timestamp}.txt"
        filepath = os.path.join(config.NOTES_DIR, filename)
        
        try:
            os.makedirs(config.NOTES_DIR, exist_ok=True)
            with open(filepath, "w") as f:
                f.write(summary)
            log_info(f"Screen summary saved to {filepath}")
            return {"success": True, "summary": summary, "path": filepath}
        except Exception as e:
            log_event("screen_to_note", "Skills", "Failure", str(e))
            return {"success": False, "error": str(e)}
            
    return {"success": False, "error": "User denied action."}

def remember_screen_context(test_mode_active=True, takecommand_func=None) -> dict:
    """Saves current screen summary to memory."""
    res = screen_reader.get_screen_context()
    if not res["success"]:
        return res

    summary = res["summary"]
    
    # Confirm before saving to memory
    if confirm_action("remember the context of your current screen", test_mode_active, takecommand_func):
        memory_db.set_preference("last_screen_context", summary)
        log_info("Screen context saved to memory preferences.")
        return {"success": True, "summary": summary}
            
    return {"success": False, "error": "User denied action."}
