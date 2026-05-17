from core.logger import log_event, log_info
from core.tts import speak
from features import apps, browser, search, notes, screenshot, music, utilities, system_monitor
from memory import memory_db
from ai import intent_classifier
from automation import screen_reader, desktop_controller
from skills import skill_manager
import config
import logging

# Initialize memory on import
memory_db.initialize_memory()

# Accessor cache for PyQt GUI and other external runners
LAST_RESPONSE_TEXT = ""
LAST_INTENT = "unknown"
LAST_SUCCESS = False
LAST_LOG_MESSAGE = ""

def get_last_response():
    global LAST_RESPONSE_TEXT, LAST_INTENT, LAST_SUCCESS, LAST_LOG_MESSAGE
    return {
        "response": LAST_RESPONSE_TEXT,
        "intent": LAST_INTENT,
        "success": LAST_SUCCESS,
        "log_message": LAST_LOG_MESSAGE,
    }

def is_looks_like_general_question(query: str) -> bool:
    """Heuristic helper to detect if a command looks like a general question or conversational text."""
    q = query.lower().strip()
    
    # Prefix matches
    prefixes = ["who is", "what is", "which is", "why", "how", "explain", "tell me about", "define"]
    for prefix in prefixes:
        if q.startswith(prefix):
            return True
            
    # Contains matches
    contains_words = ["best", "recommend"]
    for word in contains_words:
        if word in q:
            return True
            
    # Also fallback question words anywhere in string
    question_words = ["who", "what", "where", "when", "why", "how", "explain", "tell me", "define", "give me", "why does"]
    for word in question_words:
        if q.startswith(word) or f" {word} " in q:
            return True
            
    # Word count heuristic
    words = q.split()
    if len(words) >= 3:
        return True
        
    return False

def check_deterministic_keywords(query, test_mode_active, takecommand_func):
    """Checks for deterministic commands. Returns (matched, should_continue)."""
    q = query.lower().strip()
    
    # Check for skill keywords first
    if "summarize my screen and save it" in q or "read this screen and make a note" in q or "save screen summary" in q:
        return True, execute_intent("skill_summarize_screen_to_note", None, query, test_mode_active, takecommand_func)
    if "remember what is on my screen" in q or "save this screen context" in q:
        return True, execute_intent("skill_remember_screen_context", None, query, test_mode_active, takecommand_func)
    if "make a note" in q or "create note" in q:
        target_text = query.replace("make a note", "").replace("create note", "").replace(":", "").strip()
        return True, execute_intent("skill_create_note", target_text, query, test_mode_active, takecommand_func)
    if "summarize my recent activity" in q or "save my recent activity as a note" in q:
        return True, execute_intent("skill_summarize_memory_to_note", None, query, test_mode_active, takecommand_func)
    
    if "time" in q:
        return True, execute_intent("time", None, query, test_mode_active, takecommand_func)
    if "date" in q:
        return True, execute_intent("date", None, query, test_mode_active, takecommand_func)
    if "read screen" in q or "read my screen" in q or "screen read" in q:
        return True, execute_intent("screen_read", None, query, test_mode_active, takecommand_func)
    if "system status" in q or "check my system" in q or "cpu usage" in q or "ram usage" in q:
        return True, execute_intent("system_status", None, query, test_mode_active, takecommand_func)
    if "type this" in q:
        target_text = query.replace("type this", "").replace(":", "").strip()
        return True, execute_intent("automation_type_text", target_text, query, test_mode_active, takecommand_func)
    if "paste this" in q:
        target_text = query.replace("paste this", "").replace(":", "").strip()
        return True, execute_intent("automation_paste_text", target_text, query, test_mode_active, takecommand_func)
    if "press ctrl c" in q:
        return True, execute_intent("automation_hotkey", "ctrl c", query, test_mode_active, takecommand_func)
    if "press ctrl v" in q:
        return True, execute_intent("automation_hotkey", "ctrl v", query, test_mode_active, takecommand_func)
    if "click here" in q:
        return True, execute_intent("automation_click", None, query, test_mode_active, takecommand_func)
    if "wikipedia" in q:
        target_text = query.replace("wikipedia", "").strip()
        return True, execute_intent("wikipedia_search", target_text, query, test_mode_active, takecommand_func)
    if "play music" in q:
        song_name = query.replace("play music", "").strip()
        return True, execute_intent("play_music", song_name, query, test_mode_active, takecommand_func)
    
    # YouTube specific search helper
    if ("search" in q and ("in youtube" in q or "on youtube" in q or "youtube search" in q)) or "search carryminati in youtube" in q:
        search_term = query
        for phrase in ["now search", "search", "in youtube", "on youtube", "youtube"]:
            search_term = search_term.replace(phrase, "")
        search_term = search_term.replace(":", "").strip()
        
        url = f"https://www.youtube.com/results?search_query={search_term}"
        speak(f"Searching YouTube for {search_term}.")
        browser.open_website(url, query)
        response_text = f"Searching YouTube for {search_term}."
        if config.MEMORY_ENABLED:
            memory_db.save_interaction(query, response_text, "open_website", True)
        return True, True

    if "open youtube" in q:
        return True, execute_intent("open_website", "youtube.com", query, test_mode_active, takecommand_func)
    if "open google" in q:
        return True, execute_intent("open_website", "google.com", query, test_mode_active, takecommand_func)
    if "search google for" in q:
        search_term = query.replace("search google for", "").strip()
        return True, execute_intent("google_search", search_term, query, test_mode_active, takecommand_func)
    if "change your name" in q:
        return True, execute_intent("identity", None, query, test_mode_active, takecommand_func)
    if "screenshot" in q:
        return True, execute_intent("screenshot", None, query, test_mode_active, takecommand_func)
    if "look at my screen" in q or "read my screen" in q or "what is on my screen" in q or "analyze screen" in q:
        return True, execute_intent("screen_read", None, query, test_mode_active, takecommand_func)
    if "tell me a joke" in q:
        return True, execute_intent("joke", None, query, test_mode_active, takecommand_func)
    if "open" in q:
        app_name = query.replace("open", "").strip()
        return True, execute_intent("open_app", app_name, query, test_mode_active, takecommand_func)
    if "take note" in q or "write down" in q:
        return True, execute_intent("take_note", None, query, test_mode_active, takecommand_func)
    
    if "shutdown" in q:
        speak("Are you sure you want to shut down the system?")
        ans = takecommand_func(force_text=test_mode_active)
        if ans and "yes" in ans.lower():
            speak("Shutting down the system, goodbye!")
            memory_db.save_interaction(query, "Shutting down.", "exit", True)
            return True, False
        else:
            speak("Shutdown cancelled.")
            if config.MEMORY_ENABLED:
                memory_db.save_interaction(query, "Shutdown cancelled.", "exit", True)
            return True, True
            
    if "offline" in q or "exit" in q:
        speak("Going offline. Have a good day!")
        memory_db.save_interaction(query, "Going offline.", "exit", True)
        return True, False
        
    return False, True

def handle_command(query, test_mode_active=False, takecommand_func=None) -> bool:
    """Routes the query to the appropriate feature. Returns False if assistant should exit."""
    global LAST_RESPONSE_TEXT, LAST_INTENT, LAST_SUCCESS, LAST_LOG_MESSAGE
    if not query:
        return True

    # Step 1: Check for deterministic commands first (fast path)
    matched_deterministic, should_continue = check_deterministic_keywords(query, test_mode_active, takecommand_func)
    if matched_deterministic:
        return should_continue

    # Step 2: Try AI Intent Classification if enabled and credentials exist
    if config.has_llm_credentials():
        log_info(f"No deterministic keyword match. Attempting AI classification for query: [{query}]")
        try:
            # Direct general-question heuristic override:
            if is_looks_like_general_question(query):
                log_info("Direct heuristic match for general question. Routing to general chat.")
                return execute_intent("general_chat", None, query, test_mode_active, takecommand_func)

            recent_memory = memory_db.get_recent_interactions(5)
            classification = intent_classifier.classify_intent_with_llm(query, recent_memory)
            
            intent = classification.get("intent", "unknown")
            confidence = classification.get("confidence", 0.0)
            target = classification.get("target")

            log_info(f"AI Classification: intent=[{intent}], confidence=[{confidence}], target=[{target}]")

            if intent == "exit":
                return execute_intent(intent, target, query, test_mode_active, takecommand_func)
            elif intent == "general_chat":
                log_info("Routing query to general chat response.")
                return execute_intent("general_chat", target, query, test_mode_active, takecommand_func)
            elif intent != "unknown" and confidence > 0.6:
                log_info(f"Routing to safe mapped intent: [{intent}]")
                return execute_intent(intent, target, query, test_mode_active, takecommand_func)
            elif is_looks_like_general_question(query) or intent == "unknown":
                log_info("Unclassified query looks like general question. Routing to general chat.")
                return execute_intent("general_chat", target, query, test_mode_active, takecommand_func)
        except Exception as e:
            log_info(f"Error during AI routing: {e}. Falling back to default response.")

    # Step 3: Check if general question fallback is triggered but LLM is disabled or missing credentials
    if is_looks_like_general_question(query):
        if not config.LLM_ENABLED:
            response_text = "LLM is disabled in configuration. Please check LLM settings."
        elif not config.NVIDIA_API_KEY or config.NVIDIA_API_KEY == "your_actual_nvidia_key_here":
            response_text = "API key is not configured. Please add it to your .env file."
        else:
            response_text = "AI response is currently unavailable. Please check LLM settings."
        intent = "unknown"
        success = False
        speak(response_text)
        if config.MEMORY_ENABLED:
            memory_db.save_interaction(query, response_text, intent, success)
            
        # Update Cache
        LAST_RESPONSE_TEXT = response_text
        LAST_INTENT = intent
        LAST_SUCCESS = success
        LAST_LOG_MESSAGE = f"General question fallback: {response_text}"
        return True

    # Step 4: Default fallback when LLM is disabled, missing, or fails
    response_text = "No matching keyword found."
    intent = "unknown"
    success = False
    speak("I am not sure how to help with that.")
    
    if config.MEMORY_ENABLED:
        memory_db.save_interaction(query, response_text, intent, success)
        
    # Update Cache
    LAST_RESPONSE_TEXT = "I am not sure how to help with that."
    LAST_INTENT = intent
    LAST_SUCCESS = success
    LAST_LOG_MESSAGE = "No matching keyword found."
    
    return True

def execute_intent(intent, target, query, test_mode_active, takecommand_func) -> bool:
    """Executes a specific intent mapped from the AI Brain."""
    response_text = ""
    success = True
    should_continue = True

    try:
        # Check if it's a skill intent
        if intent.startswith("skill_"):
            res = skill_manager.run_skill(intent, target, query, test_mode_active, takecommand_func)
            response_text = res.get("summary") or res.get("message") or "Skill completed."
            success = res["success"]
            
        elif intent == "time":
            response_text = utilities.time()
        elif intent == "date":
            response_text = utilities.date()
        elif intent == "wikipedia_search":
            query_text = target if target else query.replace("wikipedia", "").strip()
            res = search.search_wikipedia(query_text)
            response_text = res["result"]
            success = res["success"]
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
        elif intent == "screen_read":
            speak("One moment, I am looking at your screen.")
            res = screen_reader.get_screen_context()
            if res["success"]:
                speak(res["summary"])
                print(f"[NOVA Screen Summary]: {res['summary']}")
                response_text = res["summary"]
            else:
                speak(f"Sorry, I couldn't read the screen. {res['error']}")
                response_text = f"Screen reading failed: {res['error']}"
                success = False
        elif intent == "system_status":
            summary = system_monitor.summarize_system_status()
            speak(summary)
            print(f"[System Status]: {summary}")
            response_text = summary
        elif intent == "automation_type_text":
            text = target if target else query.replace("type this", "").strip()
            res = desktop_controller.type_text(text, test_mode_active, takecommand_func)
            response_text = f"Typed text: {text}" if res["success"] else f"Typing failed: {res.get('error')}"
            success = res["success"]
        elif intent == "automation_paste_text":
            text = target if target else query.replace("paste this", "").strip()
            res = desktop_controller.paste_text(text, test_mode_active, takecommand_func)
            response_text = f"Pasted text: {text}" if res["success"] else f"Pasting failed: {res.get('error')}"
            success = res["success"]
        elif intent == "automation_copy_clipboard":
            res = desktop_controller.copy_clipboard()
            if res["success"]:
                speak("I have copied the selection to the clipboard.")
                response_text = f"Copied to clipboard: {res['text'][:50]}..."
            else:
                speak("Failed to copy selection.")
                response_text = f"Copy failed: {res.get('error')}"
                success = False
        elif intent == "automation_hotkey":
            key_map = {"ctrl c": ["ctrl", "c"], "ctrl v": ["ctrl", "v"], "ctrl a": ["ctrl", "a"], "ctrl s": ["ctrl", "s"], "alt tab": ["alt", "tab"], "escape": ["esc"], "enter": ["enter"]}
            target_key = target.lower() if target else ""
            keys = key_map.get(target_key)
            if keys:
                res = desktop_controller.press_hotkey(keys, test_mode_active, takecommand_func)
                response_text = f"Pressed hotkey: {keys}" if res["success"] else f"Hotkey failed: {res.get('error')}"
                success = res["success"]
            else:
                response_text = f"Unsupported hotkey: {target}"
                success = False
        elif intent == "automation_mouse_move":
            res = desktop_controller.move_mouse_relative(50, 0, test_mode_active, takecommand_func)
            response_text = "Moved mouse." if res["success"] else "Mouse move failed."
            success = res["success"]
        elif intent == "automation_click":
            res = desktop_controller.click_current_position(test_mode_active, takecommand_func)
            response_text = "Clicked mouse." if res["success"] else "Click failed."
            success = res["success"]
        elif intent == "general_chat":
            recent_memory = memory_db.get_recent_interactions(5)
            chat_resp = intent_classifier.generate_chat_response(query, recent_memory)
            if chat_resp:
                if chat_resp.startswith("[Error]"):
                    err_detail = chat_resp.replace("[Error]", "").strip()
                    response_text = err_detail
                    speak(f"AI response failed: {err_detail}")
                    success = False
                else:
                    speak(chat_resp)
                    print(f"[NOVA Chat]: {chat_resp}")
                    response_text = chat_resp
            else:
                response_text = "AI response is currently unavailable. Please check LLM settings."
                speak("AI response is currently unavailable. Please check LLM settings.")
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

    # Determine log message
    log_msg = f"Executed {intent}."
    if intent == "time":
        log_msg = "Told the time."
    elif intent == "date":
        log_msg = "Told the date."
    elif intent == "wikipedia_search":
        log_msg = f"Wikipedia search for {target or query}."
    elif intent == "play_music":
        log_msg = f"Playing music: {target or query}."
    elif intent == "open_website":
        log_msg = f"Opening website: {target or 'google.com'}."
    elif intent == "google_search":
        log_msg = f"Searching Google for {target or query}."
    elif intent == "open_app":
        log_msg = f"Opening app: {target or query}."
    elif intent == "screenshot":
        log_msg = "Took a screenshot."
    elif intent == "joke":
        log_msg = "Told a joke."
    elif intent == "take_note":
        log_msg = "Saved a note."
    elif intent == "remember_name":
        log_msg = f"Remembered user name."
    elif intent == "recall_name":
        log_msg = "Recalled user name."
    elif intent == "show_memory":
        log_msg = "Displayed interaction history."
    elif intent == "clear_memory":
        log_msg = "Interaction history cleared."
    elif intent == "greeting":
        log_msg = "Greeted user."
    elif intent == "screen_read":
        log_msg = "Screen reading processed."
    elif intent == "system_status":
        log_msg = "Fetched system status."
    elif intent == "automation_type_text":
        log_msg = f"Typed text."
    elif intent == "automation_paste_text":
        log_msg = f"Pasted text."
    elif intent == "automation_copy_clipboard":
        log_msg = "Copied to clipboard."
    elif intent == "automation_hotkey":
        log_msg = f"Pressed hotkey."
    elif intent == "automation_mouse_move":
        log_msg = "Moved mouse."
    elif intent == "automation_click":
        log_msg = "Clicked mouse."
    elif intent == "general_chat":
        log_msg = "Generated general chat response."
    elif intent == "exit":
        log_msg = "Going offline."

    # Save to memory
    if config.MEMORY_ENABLED:
        memory_db.save_interaction(query, response_text, intent, success)
    
    # Update globals
    global LAST_RESPONSE_TEXT, LAST_INTENT, LAST_SUCCESS, LAST_LOG_MESSAGE
    LAST_RESPONSE_TEXT = response_text
    LAST_INTENT = intent
    LAST_SUCCESS = success
    LAST_LOG_MESSAGE = log_msg
    
    return should_continue

def handle_keyword_routing(query, test_mode_active, takecommand_func) -> bool:
    """Fallback keyword-based routing logic."""
    matched_deterministic, should_continue = check_deterministic_keywords(query, test_mode_active, takecommand_func)
    if matched_deterministic:
        return should_continue
        
    response_text = "No matching keyword found."
    intent = "unknown"
    success = False
    speak("I am not sure how to help with that.")
    
    if config.MEMORY_ENABLED:
        memory_db.save_interaction(query, response_text, intent, success)
    
    return True

