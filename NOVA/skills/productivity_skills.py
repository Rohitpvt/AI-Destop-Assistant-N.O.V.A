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

from features import notes
from memory import memory_db
from core.safety import confirm_action
from core.logger import log_info, log_event
from ai import intent_classifier

def create_note_from_command(text: str) -> dict:
    """Wraps note taking with a consistent skill interface."""
    if not text:
        return {"success": False, "error": "No note content provided."}
    
    notes.take_note(text)
    return {"success": True, "message": "Note saved successfully."}

def summarize_memory_to_note(test_mode_active=True, takecommand_func=None) -> dict:
    """Summarizes recent activity and saves it to a note."""
    interactions = memory_db.get_recent_interactions(10)
    if not interactions:
        return {"success": False, "error": "No recent history found."}

    # Prepare summary
    history_text = "\n".join([f"- User: {m[1]} | NOVA: {m[2]}" for m in reversed(interactions)])
    
    summary = ""
    from config import has_llm_credentials
    if has_llm_credentials():
        prompt = f"Summarize the following recent activity into 3-5 bullet points focusing on key actions and requests:\n\n{history_text}"
        summary = intent_classifier.generate_chat_response(prompt)
    
    if not summary:
        summary = f"Summary of recent {len(interactions)} interactions:\n{history_text}"

    # Confirm before saving
    if confirm_action("save a summary of your recent activity to a note", test_mode_active, takecommand_func):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"recent_activity_{timestamp}.txt"
        filepath = os.path.join(config.NOTES_DIR, filename)
        
        try:
            os.makedirs(config.NOTES_DIR, exist_ok=True)
            with open(filepath, "w") as f:
                f.write(summary)
            log_info(f"Session summary saved to {filepath}")
            return {"success": True, "summary": summary, "path": filepath}
        except Exception as e:
            log_event("summarize_memory", "Skills", "Failure", str(e))
            return {"success": False, "error": str(e)}
            
    return {"success": False, "error": "User denied action."}
