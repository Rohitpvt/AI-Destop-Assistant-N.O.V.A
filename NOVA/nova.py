import sys
import os
import argparse
import webbrowser as wb

# Ensure the NOVA directory is in the search path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from core.logger import log_event
from core.tts import speak
from core.speech import takecommand
from core.router import handle_command
from features import utilities, apps, search, music, notes, screenshot

# Import config
try:
    import config
except ImportError:
    # Fallback handled in modules, but we keep it here for argparse or other root needs
    class config:
        DEFAULT_NAME = "NOVA"

test_mode_active = False

def run_test_menu():
    """Shows a menu for testing specific features."""
    while True:
        print(f"\n--- {config.DEFAULT_NAME} Feature Test Menu ---")
        print("[1] Test greeting")
        print("[2] Test time/date")
        print("[3] Test open website (YouTube)")
        print("[4] Test Google search")
        print("[5] Test Wikipedia search")
        print("[6] Test open app (Notepad)")
        print("[7] Test play music")
        print("[8] Test take note")
        print("[9] Test screenshot")
        print("[10] Test joke")
        print("[M] Manual Command Mode")
        print("[0] Exit Test Mode")
        
        choice = input("\nSelect an option: ").strip().lower()
        
        if choice == '1': utilities.wishme()
        elif choice == '2': utilities.time(); utilities.date()
        elif choice == '3': wb.open("youtube.com")
        elif choice == '4': 
            term = input("Search term: ")
            search.search_google(term)
        elif choice == '5':
            term = input("Wikipedia query: ")
            search.search_wikipedia(term)
        elif choice == '6': apps.open_app("notepad")
        elif choice == '7': music.play_music()
        elif choice == '8': 
            speak("What should I write down?")
            note_text = takecommand(force_text=True)
            notes.take_note(note_text)
        elif choice == '9': screenshot.take_screenshot()
        elif choice == '10': utilities.tell_joke()
        elif choice == 'm':
            print("\nEnter manual commands (e.g., 'open youtube', 'time', 'exit').")
            while True:
                query = input("Manual >> ").strip().lower()
                if query in ['exit', 'back', '0']: break
                if not handle_command(query, test_mode_active=True, takecommand_func=takecommand): break
        elif choice == '0' or choice == 'exit':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"{config.DEFAULT_NAME} Desktop Voice Assistant")
    parser.add_argument("--test", action="store_true", help="Run in terminal-based test mode")
    args = parser.parse_args()

    test_mode_active = args.test

    if test_mode_active:
        print(f"--- {config.DEFAULT_NAME} Test Mode Active ---")
        run_test_menu()
    else:
        utilities.wishme()
        while True:
            query = takecommand()
            if not handle_command(query, test_mode_active=False, takecommand_func=takecommand):
                break
