import os
import random
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
except ImportError:
    class config:
        MUSIC_DIR = os.path.expanduser("~\\Music")

from core.tts import speak
from core.logger import log_event

def play_music(song_name=None) -> None:
    """Plays music from the configured Music directory."""
    song_dir = config.MUSIC_DIR
    if not os.path.exists(song_dir):
        speak(f"Music directory not found: {song_dir}")
        log_event(f"play music {song_name}", "Music", "Failure", "Directory not found")
        return

    audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg')
    try:
        songs = [f for f in os.listdir(song_dir) if f.lower().endswith(audio_extensions)]
    except Exception as e:
        speak(f"Error accessing music directory: {e}")
        log_event(f"play music {song_name}", "Music", "Failure", str(e))
        return

    if song_name:
        songs = [song for song in songs if song_name.lower() in song.lower()]

    if songs:
        song = random.choice(songs)
        try:
            os.startfile(os.path.join(song_dir, song))
            speak(f"Playing {song}.")
            print(f"Playing {song}.")
            log_event(f"play music {song_name}", "Music", "Success")
        except Exception as e:
            speak(f"Could not play music: {e}")
            log_event(f"play music {song_name}", "Music", "Failure", str(e))
    else:
        speak("No audio files found matching your request.")
        print("No audio files found.")
        log_event(f"play music {song_name}", "Music", "Failure", "No files found")
