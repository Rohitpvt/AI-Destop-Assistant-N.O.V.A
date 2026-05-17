import time
import os
import sys
import logging

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.speech import takecommand
from core.tts import speak
from core.router import handle_command
from core.logger import log_info, log_event
import config

def is_wake_word(text: str) -> bool:
    """Checks if the recognized text matches any wake word."""
    if not text:
        return False
    text = text.lower().strip()
    return any(word in text for word in config.WAKE_WORDS)

def is_sleep_command(text: str) -> bool:
    """Checks if the recognized text matches any sleep command."""
    if not text:
        return False
    text = text.lower().strip()
    return any(word in text for word in config.SLEEP_WORDS)

def is_exit_command(text: str) -> bool:
    """Checks if the recognized text matches any exit command."""
    if not text:
        return False
    text = text.lower().strip()
    return any(word in text for word in config.EXIT_WORDS)

def run_wake_mode():
    """Main loop for always-listening wake mode."""
    log_info("Wake Mode Started. Waiting for wake word...")
    print("\n--- NOVA Wake Mode Active (Waiting for 'NOVA') ---")
    
    from core.speech import listen_once
    
    while True:
        # Step 1: Listen for wake word
        result = listen_once()
        if not result["success"]:
            # If there's an ongoing microphone/hardware error (not a timeout or unrecognizable speech),
            # log it and sleep a bit to avoid CPU spin.
            if result["error_type"] not in ["timeout", "unknown_speech"]:
                log_info(f"Wake mode listening issue: {result['message']}")
                time.sleep(2)
            else:
                time.sleep(config.WAKE_LISTEN_INTERVAL_SECONDS)
            continue
            
        query = result["text"]
        if is_exit_command(query):
            speak("Exiting wake mode. Goodbye!")
            log_info("Wake mode exited via voice command.")
            break
            
        if is_wake_word(query):
            log_info("Wake word detected.")
            speak("Yes, I am listening.")
            
            # Step 2: Listen for command
            cmd_result = listen_once()
            if not cmd_result["success"]:
                log_info(f"No command detected after wake word: {cmd_result['message']}")
                continue
                
            command = cmd_result["text"]
            if is_sleep_command(command):
                speak("Going back to sleep.")
                log_info("Returning to idle via sleep command.")
                continue
                
            if is_exit_command(command):
                speak("Shuting down. Goodbye!")
                log_info("System exit via voice command after wake.")
                break
                
            # Step 3: Route command
            log_info(f"Routing command after wake: [{command}]")
            should_continue = handle_command(command, test_mode_active=False, takecommand_func=takecommand)
            
            if not should_continue:
                log_info("System shutdown triggered by command router.")
                break
                
            print("\n--- Returning to idle (Waiting for 'NOVA') ---")
        
        # Small sleep to prevent high CPU usage
        time.sleep(config.WAKE_LISTEN_INTERVAL_SECONDS)

def run_normal_voice_mode():
    """Starts the standard continuous voice loop (Phase 1 legacy style)."""
    log_info("Normal Voice Mode Started.")
    from features import utilities
    from core.speech import listen_once
    utilities.wishme()
    
    while True:
        result = listen_once()
        if not result["success"]:
            if result["error_type"] not in ["timeout", "unknown_speech"]:
                print(f"Speech recognition error: {result['message']}")
                time.sleep(2)
            continue
            
        query = result["text"]
        should_continue = handle_command(query, test_mode_active=False, takecommand_func=takecommand)
        if not should_continue:
            break
