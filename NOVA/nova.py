import sys
import os
import argparse
import webbrowser as wb

# Ensure the NOVA directory is in the search path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from core.logger import log_event, log_info
from core.tts import speak
from core.speech import takecommand
from core.router import handle_command
from core.voice_runtime import run_wake_mode, run_normal_voice_mode, is_wake_word, is_sleep_command, is_exit_command
from ai import llm_client, intent_classifier
from automation import screen_reader, desktop_controller
from features import utilities, apps, search, music, notes, screenshot, system_monitor

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
        print("[11] Test memory (remember name)")
        print("[12] Test memory (show/clear)")
        print("[13] Test AI connection")
        print("[14] Test AI classification")
        print("[15] Test screen capture")
        print("[16] Test OCR screen reading")
        print("[17] Test full screen awareness")
        print("[18] Test system status")
        print("[19] Test active window title")
        print("[20] Test safe typing confirmation")
        print("[21] Test safe hotkey confirmation")
        print("[22] Test summarize screen to note")
        print("[23] Test remember screen context")
        print("[24] Test create note from command")
        print("[25] Test summarize recent memory to note")
        print("[26] Test wake-word matching")
        print("[27] Test sleep/exit command matching")
        print("[28] Test voice recognition once")
        print("[29] Test voice output (TTS)")
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
        elif choice == '11': 
            name = input("Enter your name to remember: ")
            handle_command(f"remember my name is {name}", test_mode_active=True, takecommand_func=takecommand)
        elif choice == '12':
            handle_command("show memory", test_mode_active=True, takecommand_func=takecommand)
            confirm = input("Clear memory? (y/n): ")
            if confirm.lower() == 'y':
                handle_command("clear memory", test_mode_active=True, takecommand_func=takecommand)
        elif choice == '13':
            if config.has_llm_credentials():
                print(f"Checking connection to {config.NVIDIA_MODEL}...")
                resp = llm_client.call_llm([{"role": "user", "content": "Say 'Connection Successful'"}])
                if resp:
                    print(f"Result: {resp}")
                else:
                    print("Connection Failed.")
            else:
                print("AI is disabled or NVIDIA_API_KEY is missing in .env")
        elif choice == '14':
            if config.has_llm_credentials():
                cmd = input("Enter command to classify: ")
                print("Classifying...")
                result = intent_classifier.classify_intent_with_llm(cmd)
                import json
                print(json.dumps(result, indent=2))
            else:
                print("AI is disabled or NVIDIA_API_KEY is missing in .env")
        elif choice == '15':
            print("Capturing screen...")
            res = screen_reader.capture_screen()
            print(f"Result: {res}")
        elif choice == '16':
            print("Running OCR on latest screen...")
            res = screen_reader.extract_text_from_screen()
            if res["success"]:
                print(f"Extracted Text:\n{res['text'][:500]}...")
            else:
                print(f"Error: {res['error']}")
        elif choice == '17':
            print("Analyzing screen...")
            res = screen_reader.get_screen_context()
            if res["success"]:
                print(f"Summary: {res['summary']}")
            else:
                print(f"Error: {res['error']}")
        elif choice == '18':
            print("Fetching system status...")
            print(system_monitor.summarize_system_status())
        elif choice == '19':
            status = system_monitor.get_system_status()
            print(f"Active Window: {status.get('active_window')}")
        elif choice == '20':
            handle_command("type this: hello from nova", test_mode_active=True, takecommand_func=takecommand)
        elif choice == '21':
            handle_command("press ctrl c", test_mode_active=True, takecommand_func=takecommand)
        elif choice == '22':
            handle_command("summarize my screen and save it", test_mode_active=True, takecommand_func=takecommand)
        elif choice == '23':
            handle_command("remember what is on my screen", test_mode_active=True, takecommand_func=takecommand)
        elif choice == '24':
            handle_command("make a note: this is a test note from NOVA", test_mode_active=True, takecommand_func=takecommand)
        elif choice == '25':
            handle_command("summarize my recent activity", test_mode_active=True, takecommand_func=takecommand)
        elif choice == '26':
            phrase = input("Enter phrase to test for wake word: ")
            print(f"Is wake word: {is_wake_word(phrase)}")
        elif choice == '27':
            phrase = input("Enter phrase to test for sleep/exit: ")
            print(f"Is sleep: {is_sleep_command(phrase)}")
            print(f"Is exit: {is_exit_command(phrase)}")
        elif choice == '28':
            print("Listening...")
            res = takecommand()
            print(f"Recognized: '{res}'")
        elif choice == '29':
            print("Testing voice output...")
            speak("NOVA voice output test successful.")
            print("Speak command finished.")
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
    parser.add_argument("--wake", action="store_true", help="Run in always-listening wake mode")
    parser.add_argument("--gui", action="store_true", help="Run in modern desktop GUI mode")
    args = parser.parse_args()

    if args.test:
        print(f"--- {config.DEFAULT_NAME} Test Mode Active ---")
        log_info("Starting NOVA in Test Mode")
        run_test_menu()
        log_info("Exiting NOVA Test Mode")
    elif args.wake:
        log_info("Starting NOVA in Wake Mode")
        run_wake_mode()
        log_info("Exiting NOVA Wake Mode")
    elif args.gui:
        log_info("Starting NOVA in GUI Mode")
        from gui.app import run_gui
        run_gui()
        log_info("Exiting NOVA GUI Mode")
    else:
        log_info("Starting NOVA in Normal Voice Mode")
        run_normal_voice_mode()
        log_info("Exiting NOVA Normal Voice Mode")
