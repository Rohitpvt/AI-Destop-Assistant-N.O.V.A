import speech_recognition as sr
import sys
import os

def takecommand(force_text=False) -> str:
    """Takes input from user, prioritizing microphone unless force_text is True."""
    if not force_text:
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                r.pause_threshold = 1
                audio = r.listen(source, timeout=5)

            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"You said: {query}")
            return query.lower()
        except Exception as e:
            print(f"\n[Microphone/PyAudio error or Timeout: {e}]")
            sys.stdout.flush()
    
    # Fallback or manual text input
    query = input("Type your command: ")
    return query.lower() if query else None
