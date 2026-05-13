import datetime
import pyjokes
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        NAME_FILE = "assistant_name.txt"
        DEFAULT_NAME = "NOVA"

from core.tts import speak
from core.logger import log_event

def time() -> None:
    """Tells the current time."""
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    speak("The current time is")
    speak(current_time)
    print("The current time is", current_time)
    log_event("time", "Time", "Success")

def date() -> None:
    """Tells the current date."""
    now = datetime.datetime.now()
    speak("The current date is")
    speak(f"{now.day} {now.strftime('%B')} {now.year}")
    print(f"The current date is {now.day}/{now.month}/{now.year}")
    log_event("date", "Date", "Success")

def load_name() -> str:
    """Loads the assistant's name from a file, or uses a default name."""
    try:
        with open(config.NAME_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return config.DEFAULT_NAME

def set_name(name_input_func) -> None:
    """Sets a new name for the assistant."""
    speak("What would you like to name me?")
    name = name_input_func()
    if name:
        with open(config.NAME_FILE, "w") as file:
            file.write(name)
        speak(f"Alright, I will be called {name} from now on.")
    else:
        speak("Sorry, I couldn't catch that.")

def tell_joke() -> None:
    """Tells a random joke."""
    joke = pyjokes.get_joke()
    speak(joke)
    print(joke)
    log_event("joke", "Joke", "Success")

def wishme() -> None:
    """Greets the user based on the time of day."""
    speak("Welcome back, sir!")
    print("Welcome back, sir!")

    hour = datetime.datetime.now().hour
    if 4 <= hour < 12:
        speak("Good morning!")
        print("Good morning!")
    elif 12 <= hour < 16:
        speak("Good afternoon!")
        print("Good afternoon!")
    elif 16 <= hour < 24:
        speak("Good evening!")
        print("Good evening!")
    else:
        speak("Good night, see you tomorrow.")

    assistant_name = load_name()
    speak(f"{assistant_name} at your service. Please tell me how may I assist you.")
    print(f"{assistant_name} at your service. Please tell me how may I assist you.")
    log_event("wishme", "Greeting", "Success")
