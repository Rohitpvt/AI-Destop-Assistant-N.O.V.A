from core.logger import log_event, log_info
from core.tts import speak
from features import apps, browser, search, notes, screenshot, music, utilities
from memory import memory_db
from ai import intent_classifier
import config
import logging

# Initialize memory on import
memory_db.initialize_memory()

def handle_command(query, test_mode_active=False, takecommand_func=None) -> bool:
    """Routes the query to the appropriate feature. Returns False if assistant should exit."""
    if not query:
        return True

    # Step 1: Try AI Intent Classification if enabled
    if config.has_llm_credentials():
        log_info(f"Attempting AI classification for query: [{query}]")
        recent_memory = memory_db.get_recent_interactions(5) # Pass last 5 interactions for context
        classification = intent_classifier.classify_intent_with_llm(query, recent_memory)
        
        intent = classification.get("intent", "unknown")
        confidence = classification.get("confidence", 0.0)
        target = classification.get("target")

        if confidence > 0.7 and intent != "unknown":
            log_info(f"AI Classification Success: [{intent}] with confidence [{confidence}]")
            return execute_intent(intent, target, query, test_mode_active, takecommand_func)
        else:
            log_info(f"AI Classification low confidence ({confidence}) or unknown intent. Falling back to keyword router.")

    # Step 2: Fallback to Keyword Router
    return handle_keyword_routing(query, test_mode_active, takecommand_func)

def execute_intent(intent, target, query, test_mode_active, takecommand_func) -> bool:
    """Executes a specific intent mapped from the AI Brain."""
    response_text = ""
    success = True
    should_continue = True

    try:
        if intent == "time":
            utilities.time()
            response_text = "Told the time."
        elif intent == "date":
            utilities.date()
            response_text = "Told the date."
        elif intent == "wikipedia_search":
            query_text = target if target else query.replace("wikipedia", "").strip()
            search.search_wikipedia(query_text)
            response_text = f"Searched Wikipedia for {query_text}."
        elif intent == "play_music":
            song_name = target if target else query.replace("play music", "").strip()
            music.play_music(song_name)
            response_text = f"Playing music: {song_name}."
        elif intent == "open_website":
            url = target if target else "google.com"
            browser.open_website(url, query)
            response_text = f"Opening website: {url}."
        elif intent == "google_search":
            search_term = target if target else query.replace("search google for", "").strip()
            search.search_google(search_term)
            response_text = f"Searching Google for {search_term}."
        elif intent == "open_app":
            app_name = target if target else query.replace("open", "").strip()
            apps.open_app(app_name)
            response_text = f"Opening app: {app_name}."
        elif intent == "screenshot":
            screenshot.take_screenshot()
            speak("I've taken screenshot, please check it")
            response_text = "Took a screenshot."
        elif intent == "joke":
            utilities.tell_joke()
            response_text = "Told a joke."
        elif intent == "take_note":
            speak("What should I write down?")
            note_text = takecommand_func(force_text=test_mode_active)
            notes.take_note(note_text)
            response_text = "Saved a note."
        elif intent == "remember_name":
            name = target if target else query.replace("remember my name is", "").strip()
            memory_db.set_preference("user_name", name)
            speak(f"Alright, I will remember that your name is {name}.")
            response_text = f"Remembered user name: {name}."
        elif intent == "recall_name":
            name = memory_db.get_preference("user_name")
            if name:
                speak(f"Your name is {name}.")
                response_text = f"Recalled user name: {name}."
            else:
                speak("I don't know your name yet.")
                response_text = "Name not found in memory."
        elif intent == "show_memory":
            interactions = memory_db.get_recent_interactions(config.MEMORY_MAX_RECENT)
            if interactions:
                print("\n--- Recent Interactions ---")
                for timestamp, cmd, resp, intent_tag in reversed(interactions):
                    print(f"[{timestamp}] User: {cmd} | NOVA: {resp} ({intent_tag})")
                speak("History displayed in terminal.")
                response_text = "Displayed interaction history."
            else:
                speak("Memory is empty.")
                response_text = "Interaction history empty."
        elif intent == "clear_memory":
            memory_db.clear_interactions()
            speak("Memory cleared.")
            response_text = "Interaction history cleared."
        elif intent == "greeting":
            utilities.wishme()
            response_text = "Greeted user."
        elif intent == "general_chat":
            recent_memory = memory_db.get_recent_interactions(5)
            chat_resp = intent_classifier.generate_chat_response(query, recent_memory)
            if chat_resp:
                speak(chat_resp)
                print(f"[NOVA Chat]: {chat_resp}")
                response_text = chat_resp
            else:
                response_text = "LLM failed to generate chat response."
                success = False
        elif intent == "exit":
            speak("Going offline. Have a good day!")
            memory_db.save_interaction(query, "Going offline.", intent, True)
            return False
        else:
            success = False
            response_text = "Unknown intent execution failed."
            should_continue = handle_keyword_routing(query, test_mode_active, takecommand_func)
    
    except Exception as e:
        success = False
        response_text = f"Execution error: {str(e)}"
        log_event(query, intent, "Failure", str(e))

    # Save to memory
    if config.MEMORY_ENABLED:
        memory_db.save_interaction(query, response_text, intent, success)
    
    return should_continue

def handle_keyword_routing(query, test_mode_active, takecommand_func) -> bool:
    """Fallback keyword-based routing logic."""
    response_text = ""
    intent = "unknown"
    success = True

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
    elif "offline" in query or "exit" in query:
        intent = "exit"
        speak("Going offline. Have a good day!")
        memory_db.save_interaction(query, "Going offline.", intent, True)
        return False
    else:
        intent = "unknown"
        response_text = "No matching keyword found."
        success = False
        speak("I am not sure how to help with that. Try a clearer command or check my guide.")

    # Save to memory
    if config.MEMORY_ENABLED:
        memory_db.save_interaction(query, response_text, intent, success)
    
    return True
