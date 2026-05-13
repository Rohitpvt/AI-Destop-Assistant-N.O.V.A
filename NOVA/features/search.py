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
    except wikipedia.exceptions.DisambiguationError:
        speak("Multiple results found. Please be more specific.")
        log_event(f"wikipedia {query}", "Wikipedia", "Failure", "Disambiguation")
    except Exception as e:
        speak(f"I couldn't find anything on Wikipedia for {query}.")
        log_event(f"wikipedia {query}", "Wikipedia", "Failure", str(e))

def search_google(query):
    """Performs a Google search."""
    wb.open(f"google.com/search?q={query}")
    log_event(f"search google for {query}", "Google Search", "Success")
