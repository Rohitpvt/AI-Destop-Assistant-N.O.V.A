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
            
            from core.tts import speech_suppressed, speak_response
            from core.router import get_last_response
            
            with speech_suppressed():
                success = handle_command(self.query, test_mode_active=False, takecommand_func=takecommand)
            
            result = get_last_response()
            resp = result.get("response", "")
            
            self.finished.emit(resp, success)
            
            if resp:
                speak_response(resp)
        except Exception as e:
            err_msg = f"Command execution failed: {e}"
            log_error(f"{err_msg}\n{traceback.format_exc()}")
            self.error_occurred.emit(err_msg)

class VoiceWorker(QThread):
    """Background worker to handle voice recognition."""
    recognized = pyqtSignal(dict)
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            self.status_update.emit("Listening...")
            from core.speech import listen_once
            result = listen_once()
            self.recognized.emit(result)
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
            from core.speech import listen_once
            import config
            import time

            self.status_update.emit("Wake Mode Active")
            
            while self.running:
                try:
                    result = listen_once()
                    if not result["success"]:
                        # Log microphone/connection errors to help debugging, but don't crash
                        if result["error_type"] not in ["timeout", "unknown_speech"]:
                            log_error(f"Wake mode listening warning: {result['message']}")
                        time.sleep(1)
                        continue

                    query = result["text"]
                    if is_exit_command(query):
                        self.status_update.emit("Exiting...")
                        break
                        
                    if is_wake_word(query):
                        self.status_update.emit("I'm listening...")
                        speak("Yes, I am listening.")
                        
                        cmd_result = listen_once()
                        if cmd_result["success"]:
                            command = cmd_result["text"]
                            if is_sleep_command(command):
                                speak("Going back to sleep.")
                                self.status_update.emit("Wake Mode Active")
                                continue
                            
                            self.command_detected.emit(command)
                        else:
                            log_info(f"Wake command listen failed: {cmd_result['message']}")
                        
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

class ContinuousVoiceWorker(QThread):
    """Background worker to continuously listen to the microphone for commands."""
    status = pyqtSignal(str)   # status updates
    recognized = pyqtSignal(str)  # recognized text
    response = pyqtSignal(str, str) # query, response
    log = pyqtSignal(str)      # live logs
    error = pyqtSignal(str)    # errors

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        try:
            from core.speech import listen_once
            from core.tts import speech_suppressed, speak_response
            from core.router import handle_command, get_last_response
            
            self.status.emit("Listening...")
            self.log.emit("Continuous always-listening mode started.")
            
            while self.running:
                try:
                    # Listen with 5 second timeout and 10 second phrase limit
                    result = listen_once(timeout=5, phrase_time_limit=10)
                    if not self.running:
                        break
                        
                    if not result["success"]:
                        # Simply log the silence or timeout to Live Logs, don't show on main chat
                        self.log.emit(f"Microphone status: {result.get('message', 'Timeout')}")
                        continue
                        
                    query = result["text"].strip()
                    if not query:
                        continue
                        
                    # Preprocess command to strip wake word if present
                    query_clean = query
                    for w in ["hey nova", "wake up nova", "nova"]:
                        if query_clean.lower().startswith(w):
                            query_clean = query_clean[len(w):].strip()
                            break
                            
                    if not query_clean:
                        continue
                        
                    # Emit recognized query
                    self.recognized.emit(query)
                    self.status.emit("Thinking...")
                    self.log.emit(f"Recognized speech: [{query}]")
                    
                    # Execute command in suppressed speech context to avoid double-speaking
                    with speech_suppressed():
                        success = handle_command(query_clean, test_mode_active=False)
                        
                    # Fetch response from cache
                    resp_result = get_last_response()
                    resp = resp_result.get("response", "")
                    
                    # Emit query and response to update chat history
                    self.response.emit(query, resp)
                    self.log.emit(f"Command executed. Success: {success}")
                    
                    # Speak response aloud exactly once
                    if resp:
                        speak_response(resp)
                        
                    # Resume listening
                    self.status.emit("Listening...")
                    
                except Exception as inner_ex:
                    self.log.emit(f"Error in continuous listening loop iteration: {inner_ex}")
                    self.status.emit("Listening...")
                    
                import time
                time.sleep(0.5)
                
            self.status.emit("Idle")
            self.log.emit("Continuous always-listening mode stopped.")
            
        except Exception as e:
            self.error.emit(f"Fatal error in voice thread: {e}")
            
    def stop(self):
        self.running = False

