from core.logger import log_event
from core.tts import speak
from features import apps, browser, search, notes, screenshot, music, utilities

def handle_command(query, test_mode_active=False, takecommand_func=None) -> bool:
    """Routes the query to the appropriate feature. Returns False if assistant should exit."""
    if not query:
        return True

    if "time" in query:
        utilities.time()
    elif "date" in query:
        utilities.date()
    elif "wikipedia" in query:
        query_text = query.replace("wikipedia", "").strip()
        search.search_wikipedia(query_text)
    elif "play music" in query:
        song_name = query.replace("play music", "").strip()
        music.play_music(song_name)
    elif "open youtube" in query:
        browser.open_website("youtube.com", query)
    elif "open google" in query:
        browser.open_website("google.com", query)
    elif "search google for" in query:
        search_term = query.replace("search google for", "").strip()
        search.search_google(search_term)
    elif "change your name" in query:
        # Pass the takecommand function to set_name to handle input
        utilities.set_name(lambda: takecommand_func(force_text=test_mode_active))
    elif "screenshot" in query:
        screenshot.take_screenshot()
        speak("I've taken screenshot, please check it")
    elif "tell me a joke" in query:
        utilities.tell_joke()
    elif "open" in query:
        app_name = query.replace("open", "").strip()
        apps.open_app(app_name)
    elif "take note" in query or "write down" in query:
        # We need the note text. If not in query, we might need another takecommand call.
        # For simplicity, we keep the original logic which calls takecommand again.
        speak("What should I write down?")
        note_text = takecommand_func(force_text=test_mode_active)
        notes.take_note(note_text)
    elif "shutdown" in query:
        speak("Are you sure you want to shut down the system?")
        ans = takecommand_func(force_text=test_mode_active)
        if ans and "yes" in ans:
            speak("Shutting down the system, goodbye!")
            log_event(query, "Power", "Success (Mocked)")
            return False
        else:
            speak("Shutdown cancelled.")
    elif "restart" in query:
        speak("Are you sure you want to restart the system?")
        ans = takecommand_func(force_text=test_mode_active)
        if ans and "yes" in ans:
            speak("Restarting the system, please wait!")
            log_event(query, "Power", "Success (Mocked)")
            return False
        else:
            speak("Restart cancelled.")
    elif "offline" in query or "exit" in query:
        speak("Going offline. Have a good day!")
        log_event(query, "Exit", "Success")
        return False
    else:
        log_event(query, "Unknown", "Ignored")
    
    return True
