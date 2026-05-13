from PyQt5.QtCore import QThread, pyqtSignal
import os
import sys

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.router import handle_command
from core.speech import takecommand
from core.logger import log_info

class CommandWorker(QThread):
    """Background worker to execute commands without freezing the GUI."""
    finished = pyqtSignal(str, bool)  # response_text, success
    status_update = pyqtSignal(str)   # status message

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        self.status_update.emit("Thinking...")
        log_info(f"GUI Command Execution: [{self.query}]")
        
        # Capture the last memory response or use a result from handle_command if we modify it
        # For now, we rely on the fact that handle_command saves to memory
        success = handle_command(self.query, test_mode_active=False, takecommand_func=takecommand)
        
        # We don't easily get the response_text back from the current router structure 
        # unless we fetch it from memory or update the router.
        # Let's fetch the very last response from memory
        from memory import memory_db
        interactions = memory_db.get_recent_interactions(1)
        resp = interactions[0][2] if interactions else "Command processed."
        
        self.finished.emit(resp, success)

class VoiceWorker(QThread):
    """Background worker to handle voice recognition."""
    recognized = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def run(self):
        self.status_update.emit("Listening...")
        query = takecommand()
        self.recognized.emit(query)

class WakeWorker(QThread):
    """Background worker to run the wake mode loop."""
    status_update = pyqtSignal(str)
    command_detected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        from core.voice_runtime import is_wake_word, is_sleep_command, is_exit_command
        from core.tts import speak
        import config
        import time

        self.status_update.emit("Wake Mode Active")
        
        while self.running:
            query = takecommand()
            
            if is_exit_command(query):
                self.status_update.emit("Exiting...")
                break
                
            if is_wake_word(query):
                self.status_update.emit("I'm listening...")
                speak("Yes, I am listening.")
                
                command = takecommand()
                if command:
                    if is_sleep_command(command):
                        speak("Going back to sleep.")
                        self.status_update.emit("Wake Mode Active")
                        continue
                    
                    self.command_detected.emit(command)
                
                self.status_update.emit("Wake Mode Active")
            
            time.sleep(1)

    def stop(self):
        self.running = False
