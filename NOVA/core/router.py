from core.logger import log_event
from core.tts import speak
from features import apps, browser, search, notes, screenshot, music, utilities
from memory import memory_db
import config

# Initialize memory on import
memory_db.initialize_memory()

def handle_command(query, test_mode_active=False, takecommand_func=None) -> bool:
    """Routes the query to the appropriate feature. Returns False if assistant should exit."""
    if not query:
        return True

    response_text = ""
    intent = "unknown"
    success = True

    try:
        if "time" in query:
            intent = "time"
            utilities.time()
            response_text = "Told the time."
        elif "date" in query:
            intent = "date"
            utilities.date()
            response_text = "Told the date."
        elif "wikipedia" in query:
            intent = "wikipedia"
            query_text = query.replace("wikipedia", "").strip()
            search.search_wikipedia(query_text)
            response_text = f"Searched Wikipedia for {query_text}."
        elif "play music" in query:
            intent = "music"
            song_name = query.replace("play music", "").strip()
            music.play_music(song_name)
            response_text = f"Playing music: {song_name}."
        elif "open youtube" in query:
            intent = "website"
            browser.open_website("youtube.com", query)
            response_text = "Opening YouTube."
        elif "open google" in query:
            intent = "website"
            browser.open_website("google.com", query)
            response_text = "Opening Google."
        elif "search google for" in query:
            intent = "search"
            search_term = query.replace("search google for", "").strip()
            search.search_google(search_term)
            response_text = f"Searching Google for {search_term}."
        elif "change your name" in query:
            intent = "identity"
            utilities.set_name(lambda: takecommand_func(force_text=test_mode_active))
            response_text = "Changing assistant name."
        elif "screenshot" in query:
            intent = "screenshot"
            screenshot.take_screenshot()
            speak("I've taken screenshot, please check it")
            response_text = "Took a screenshot."
        elif "tell me a joke" in query:
            intent = "joke"
            utilities.tell_joke()
            response_text = "Told a joke."
        elif "open" in query:
            intent = "app"
            app_name = query.replace("open", "").strip()
            apps.open_app(app_name)
            response_text = f"Opening app: {app_name}."
        elif "take note" in query or "write down" in query:
            intent = "note"
            speak("What should I write down?")
            note_text = takecommand_func(force_text=test_mode_active)
            notes.take_note(note_text)
            response_text = "Saved a note."
        
        # --- Memory Commands ---
        elif "remember my name is" in query:
            intent = "memory_save_name"
            name = query.replace("remember my name is", "").strip()
            if name:
                memory_db.set_preference("user_name", name)
                speak(f"Alright, I will remember that your name is {name}.")
                response_text = f"Remembered user name: {name}."
            else:
                speak("I didn't catch the name. Could you say it again?")
                response_text = "Failed to remember name (no input)."
        
        elif "what is my name" in query:
            intent = "memory_get_name"
            name = memory_db.get_preference("user_name")
            if name:
                speak(f"Your name is {name}.")
                response_text = f"Recalled user name: {name}."
            else:
                speak("I don't know your name yet. You can tell me by saying 'remember my name is ...'.")
                response_text = "User name not found in memory."
        
        elif "show memory" in query:
            intent = "memory_show"
            interactions = memory_db.get_recent_interactions(config.MEMORY_MAX_RECENT)
            if interactions:
                speak(f"Showing last {len(interactions)} interactions in the terminal.")
                print("\n--- Recent Interactions ---")
                for timestamp, cmd, resp, intent_tag in reversed(interactions):
                    print(f"[{timestamp}] User: {cmd} | NOVA: {resp} ({intent_tag})")
                response_text = "Displayed interaction history."
            else:
                speak("Memory is empty.")
                response_text = "Interaction history empty."
        
        elif "clear memory" in query:
            intent = "memory_clear"
            speak("Are you sure you want to clear your interaction history?")
            ans = takecommand_func(force_text=test_mode_active)
            if ans and "yes" in ans:
                memory_db.clear_interactions()
                speak("Memory cleared.")
                response_text = "Interaction history cleared."
            else:
                speak("Memory clear cancelled.")
                response_text = "Memory clear cancelled by user."

        elif "shutdown" in query:
            intent = "power"
            speak("Are you sure you want to shut down the system?")
            ans = takecommand_func(force_text=test_mode_active)
            if ans and "yes" in ans:
                speak("Shutting down the system, goodbye!")
                memory_db.save_interaction(query, "Shutting down.", intent, True)
                return False
            else:
                speak("Shutdown cancelled.")
                response_text = "Shutdown cancelled."
        elif "restart" in query:
            intent = "power"
            speak("Are you sure you want to restart the system?")
            ans = takecommand_func(force_text=test_mode_active)
            if ans and "yes" in ans:
                speak("Restarting the system, please wait!")
                memory_db.save_interaction(query, "Restarting.", intent, True)
                return False
            else:
                speak("Restart cancelled.")
                response_text = "Restart cancelled."
        elif "offline" in query or "exit" in query:
            intent = "exit"
            speak("Going offline. Have a good day!")
            memory_db.save_interaction(query, "Going offline.", intent, True)
            return False
        else:
            intent = "unknown"
            response_text = "No matching feature found."
            success = False
    
    except Exception as e:
        success = False
        response_text = f"Error: {str(e)}"
        log_event(query, intent, "Failure", str(e))

    # Save to memory
    if config.MEMORY_ENABLED:
        memory_db.save_interaction(query, response_text, intent, success)
    
    return True
