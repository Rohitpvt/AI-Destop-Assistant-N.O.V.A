import wikipedia
import webbrowser as wb
from core.tts import speak
from core.logger import log_event

def search_wikipedia(query):
    """Searches Wikipedia and returns a summary."""
    try:
        speak("Searching Wikipedia...")
        result = wikipedia.summary(query, sentences=2)
        speak(result)
        print(result)
        log_event(f"wikipedia {query}", "Wikipedia", "Success")
        return {"success": True, "result": result}
    except wikipedia.exceptions.DisambiguationError:
        err = "Multiple results found. Please be more specific."
        speak(err)
        log_event(f"wikipedia {query}", "Wikipedia", "Failure", "Disambiguation")
        return {"success": False, "result": err}
    except Exception as e:
        err = f"I couldn't find anything on Wikipedia for {query}."
        speak(err)
        log_event(f"wikipedia {query}", "Wikipedia", "Failure", str(e))
        return {"success": False, "result": err}

def search_google(query):
    """Performs a Google search."""
    wb.open(f"google.com/search?q={query}")
    log_event(f"search google for {query}", "Google Search", "Success")
