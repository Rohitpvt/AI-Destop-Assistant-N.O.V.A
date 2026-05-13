from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
import os
import sys
import traceback
import logging

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.router import handle_command
from core.speech import takecommand
from core.logger import log_info, log_error

class ConfirmationRequester(QObject):
    """Bridge to request confirmation from the main thread."""
    request_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.result = False

    def confirm(self, description):
        """Emits signal and waits for the slot to finish (BlockingQueuedConnection)."""
        self.request_signal.emit(description)
        return self.result

# Singleton instance for the safety module to call
confirmation_bridge = ConfirmationRequester()

class CommandWorker(QThread):
    """Background worker to execute commands without freezing the GUI."""
    finished = pyqtSignal(str, bool)  # response_text, success
    status_update = pyqtSignal(str)   # status message
    error_occurred = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            self.status_update.emit("Thinking...")
            log_info(f"GUI Command Execution: [{self.query}]")
            
            success = handle_command(self.query, test_mode_active=False, takecommand_func=takecommand)
            
            from memory import memory_db
            interactions = memory_db.get_recent_interactions(1)
            resp = interactions[0][2] if interactions else "Command processed."
            
            self.finished.emit(resp, success)
        except Exception as e:
            err_msg = f"Command execution failed: {e}"
            log_error(f"{err_msg}\n{traceback.format_exc()}")
            self.error_occurred.emit(err_msg)

class VoiceWorker(QThread):
    """Background worker to handle voice recognition."""
    recognized = pyqtSignal(str)
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            self.status_update.emit("Listening...")
            query = takecommand()
            self.recognized.emit(query)
        except Exception as e:
            err_msg = f"Voice recognition failed: {e}"
            log_error(f"{err_msg}\n{traceback.format_exc()}")
            self.error_occurred.emit(err_msg)

class WakeWorker(QThread):
    """Background worker to run the wake mode loop."""
    status_update = pyqtSignal(str)
    command_detected = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        try:
            from core.voice_runtime import is_wake_word, is_sleep_command, is_exit_command
            from core.tts import speak
            import config
            import time

            self.status_update.emit("Wake Mode Active")
            
            while self.running:
                try:
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
                except Exception as inner_e:
                    log_error(f"Error in wake loop iteration: {inner_e}")
                    time.sleep(2) # Prevent rapid fire error loops
                
                time.sleep(1)
        except Exception as e:
            err_msg = f"Wake mode fatal error: {e}"
            log_error(f"{err_msg}\n{traceback.format_exc()}")
            self.error_occurred.emit(err_msg)

    def stop(self):
        self.running = False
