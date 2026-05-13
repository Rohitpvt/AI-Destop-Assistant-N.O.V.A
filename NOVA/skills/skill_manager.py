import os
import sys
import logging

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        SKILLS_ENABLED = True
        MAX_SKILL_STEPS = 5

from core.logger import log_info, log_event
from core.tts import speak
from skills import screen_skills, productivity_skills

def run_skill(intent, target, query, test_mode_active=True, takecommand_func=None) -> dict:
    """Executes a multi-step skill based on the mapped intent."""
    if not config.SKILLS_ENABLED:
        return {"success": False, "error": "Skill system is disabled."}

    log_info(f"Skill Execution Started: {intent}")
    
    result = {"success": False, "error": "Unknown skill."}

    if intent == "skill_summarize_screen_to_note":
        result = screen_skills.summarize_screen_to_note(test_mode_active, takecommand_func)
    elif intent == "skill_remember_screen_context":
        result = screen_skills.remember_screen_context(test_mode_active, takecommand_func)
    elif intent == "skill_create_note":
        text = target if target else query.replace("make a note", "").replace("create note", "").strip()
        result = productivity_skills.create_note_from_command(text)
    elif intent == "skill_summarize_memory_to_note":
        result = productivity_skills.summarize_memory_to_note(test_mode_active, takecommand_func)

    if result["success"]:
        log_info(f"Skill Execution Success: {intent}")
        if "summary" in result:
             # Speak a portion of the summary
             speak(f"Skill completed. Summary: {result['summary'][:150]}...")
        elif "message" in result:
             speak(result["message"])
    else:
        log_event(intent, "Skill Manager", "Failure", result.get("error"))
        if result.get("error") != "User denied action.":
            speak(f"Skill failed: {result.get('error')}")

    return result
