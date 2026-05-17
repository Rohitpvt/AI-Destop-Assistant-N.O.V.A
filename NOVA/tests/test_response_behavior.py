import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import datetime

# Add the parent directory and NOVA directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.router import handle_command, get_last_response
from memory import memory_db
from gui.worker import CommandWorker
from core.tts import (
    speak_response, 
    speak, 
    speech_suppressed, 
    is_speaking_suppressed, 
    suppress_speaking
)
import config

class TestResponseBehavior(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Ensure memory is initialized
        config.MEMORY_ENABLED = True
        memory_db.initialize_memory()
        
    def setUp(self):
        # Clear interactions before each test to have clean state
        memory_db.clear_interactions()
        # Reset thread suppression state
        suppress_speaking(False)
        config.VOICE_OUTPUT_ENABLED = True
        
    @patch('core.tts.speak')
    def test_time_command_stores_and_exposes_actual_time(self, mock_speak):
        """1. Verify that 'what is the time right now' stores and exposes actual time response."""
        # Execute time command
        success = handle_command("what is the time right now", test_mode_active=True, takecommand_func=lambda: "exit")
        self.assertTrue(success)
        
        # Check cache
        result = get_last_response()
        self.assertEqual(result["intent"], "time")
        self.assertEqual(result["log_message"], "Told the time.")
        self.assertTrue(result["response"].startswith("The current time is "))
        self.assertTrue(result["response"].endswith(" AM.") or result["response"].endswith(" PM."))
        
        # Check memory
        interactions = memory_db.get_recent_interactions(1)
        self.assertTrue(len(interactions) > 0)
        self.assertEqual(interactions[0][2], result["response"])

    @patch('core.tts.speak')
    def test_date_command_stores_and_exposes_actual_date(self, mock_speak):
        """2. Verify that 'what is the date today' stores and exposes actual date response."""
        # Execute date command
        success = handle_command("what is the date today", test_mode_active=True, takecommand_func=lambda: "exit")
        self.assertTrue(success)
        
        # Check cache
        result = get_last_response()
        self.assertEqual(result["intent"], "date")
        self.assertEqual(result["log_message"], "Told the date.")
        self.assertTrue(result["response"].startswith("Today is "))
        now = datetime.datetime.now()
        year_str = str(now.year)
        self.assertTrue(result["response"].endswith(year_str + "."))
        
        # Check memory
        interactions = memory_db.get_recent_interactions(1)
        self.assertTrue(len(interactions) > 0)
        self.assertEqual(interactions[0][2], result["response"])

    @patch('core.tts.speak')
    def test_get_last_response_accessor(self, mock_speak):
        """3. Verify get_last_response() returns actual response after handle_command()."""
        handle_command("what is the time right now", test_mode_active=True, takecommand_func=lambda: "exit")
        result = get_last_response()
        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
        self.assertEqual(result["intent"], "time")
        self.assertTrue(result["response"].startswith("The current time is "))

    @patch('core.tts.speak')
    @patch('ai.llm_client.call_llm')
    def test_general_question_calls_mocked_llm_fallback(self, mock_call_llm, mock_speak):
        """4. Verify that general question calls mocked LLM fallback."""
        mock_call_llm.return_value = "Python is a high-level programming language."
        
        with patch('config.has_llm_credentials', return_value=True), \
             patch('config.LLM_ENABLED', True):
            
            success = handle_command("what is Python", test_mode_active=True, takecommand_func=lambda: "exit")
            self.assertTrue(success)
            self.assertTrue(mock_call_llm.called)
            
            result = get_last_response()
            self.assertEqual(result["response"], "Python is a high-level programming language.")
            self.assertEqual(result["intent"], "general_chat")

    @patch('core.tts.speak')
    def test_api_missing_gives_clear_user_facing_error(self, mock_speak):
        """5. Verify that API missing case gives clear user-facing error."""
        with patch('config.LLM_ENABLED', True), \
             patch('config.NVIDIA_API_KEY', ""):
            
            success = handle_command("explain quantum mechanics", test_mode_active=True, takecommand_func=lambda: "exit")
            self.assertTrue(success)
            
            result = get_last_response()
            self.assertEqual(result["response"], "API key is not configured. Please add it to your .env file.")
            self.assertFalse(result["success"])

    @patch('core.tts.speak')
    def test_memory_stores_actual_response_not_generic_status(self, mock_speak):
        """6. Verify that memory stores actual response text, not generic status text."""
        handle_command("what is the date today", test_mode_active=True, takecommand_func=lambda: "exit")
        
        interactions = memory_db.get_recent_interactions(1)
        self.assertTrue(len(interactions) > 0)
        self.assertNotEqual(interactions[0][2], "Told the date.")
        self.assertTrue(interactions[0][2].startswith("Today is "))

    @patch('core.tts.speak_response')
    @patch('core.tts.speak')
    def test_gui_worker_uses_get_last_response_for_chat(self, mock_speak, mock_speak_response):
        """7. Verify GUI worker uses get_last_response()[\"response\"] for the chat display."""
        worker = CommandWorker("what is the time right now")
        
        # Connect to a slot to verify emitted string
        emitted_resp = None
        emitted_success = None
        def on_finished(resp, success):
            nonlocal emitted_resp, emitted_success
            emitted_resp = resp
            emitted_success = success
            
        worker.finished.connect(on_finished)
        worker.run()
        
        self.assertIsNotNone(emitted_resp)
        self.assertTrue(emitted_success)
        self.assertTrue(emitted_resp.startswith("The current time is "))
        self.assertNotEqual(emitted_resp, "Told the time.")

    @patch('core.tts.speak')
    def test_speak_response_bridges_user_facing_responses(self, mock_speak):
        """8. Verify speak_response speaks final user-facing responses."""
        speak_response("The current time is 04:07 AM.")
        mock_speak.assert_called_once_with("The current time is 04:07 AM.")

    @patch('core.tts.speak')
    def test_speak_response_ignores_log_messages(self, mock_speak):
        """9. Verify speak_response ignores internal developer log status messages."""
        speak_response("Told the time.")
        speak_response("Told the date.")
        speak_response("Command executed successfully.")
        mock_speak.assert_not_called()

    @patch('core.tts.speak')
    def test_speak_response_respects_voice_output_enabled(self, mock_speak):
        """10. Verify speak_response respects VOICE_OUTPUT_ENABLED configuration."""
        config.VOICE_OUTPUT_ENABLED = False
        speak_response("This should not be spoken.")
        mock_speak.assert_not_called()

    def test_speech_suppression_context_manager(self):
        """11. Verify speech_suppressed context manager suppresses and restores states correctly."""
        self.assertFalse(is_speaking_suppressed())
        
        with speech_suppressed():
            self.assertTrue(is_speaking_suppressed())
            
        self.assertFalse(is_speaking_suppressed())

        # Verify always restores suppression even on exceptions
        try:
            with speech_suppressed():
                self.assertTrue(is_speaking_suppressed())
                raise ValueError("Dummy Error")
        except ValueError:
            pass
            
        self.assertFalse(is_speaking_suppressed())

    @patch('core.tts.speak_response')
    @patch('core.tts.speak')
    def test_gui_worker_triggers_speak_response_and_suppresses_internals(self, mock_speak, mock_speak_response):
        """12. Verify GUI CommandWorker suppresses internal speaking and invokes speak_response exactly once."""
        worker = CommandWorker("what is the time right now")
        worker.run()
        
        # Verify that speak() itself was suppressed/not called directly by the utility
        mock_speak.assert_not_called()
        
        # Verify that speak_response was invoked exactly once with the final time response
        mock_speak_response.assert_called_once()
        args, kwargs = mock_speak_response.call_args
        self.assertTrue(args[0].startswith("The current time is "))

    @patch('core.speech.listen_once')
    @patch('core.router.handle_command')
    @patch('core.tts.speak_response')
    def test_continuous_voice_worker_flow(self, mock_speak_response, mock_handle_command, mock_listen_once):
        """13. Verify ContinuousVoiceWorker flow executes command, emits signals and calls speak_response."""
        from gui.worker import ContinuousVoiceWorker
        
        # Setup mock behavior
        mock_listen_once.side_effect = [
            {"success": True, "text": "nova what is the time", "error_type": None, "message": "Success"},
            {"success": False, "error_type": "timeout", "message": "Silence"} # exits/loop continues
        ]
        mock_handle_command.return_value = True
        
        worker = ContinuousVoiceWorker()
        
        # Connect signals
        emitted_recognized = []
        emitted_response = []
        
        worker.recognized.connect(emitted_recognized.append)
        worker.response.connect(lambda q, r: emitted_response.append((q, r)))
        
        # Run worker loop safely for a brief moment, then stop
        def stop_worker():
            worker.stop()
            
        # Stop worker after first iteration
        worker.recognized.connect(lambda _: stop_worker())
        
        worker.run()
        
        self.assertIn("what is the time", emitted_recognized)
        mock_handle_command.assert_called_once_with("what is the time", test_mode_active=False)
        mock_speak_response.assert_called_once()

    @patch('core.speech.listen_once')
    @patch('core.router.handle_command')
    def test_continuous_voice_worker_timeout_does_not_crash(self, mock_handle_command, mock_listen_once):
        """14. Verify ContinuousVoiceWorker logs timeouts and continues looping without crashing."""
        from gui.worker import ContinuousVoiceWorker
        
        # First iteration: timeout. Second iteration: success. Then stop.
        mock_listen_once.side_effect = [
            {"success": False, "error_type": "timeout", "message": "Silence"},
            {"success": True, "text": "what is the date today", "error_type": None, "message": "Success"}
        ]
        
        worker = ContinuousVoiceWorker()
        recognized_calls = []
        worker.recognized.connect(recognized_calls.append)
        worker.recognized.connect(lambda _: worker.stop())
        
        worker.run()
        
        # Verify handle_command was called for the second success item
        mock_handle_command.assert_called_once()
        self.assertEqual(len(recognized_calls), 1)
        self.assertEqual(recognized_calls[0], "what is the date today")

    def test_continuous_voice_worker_respects_stop(self):
        """15. Verify calling .stop() successfully terminates the run loop."""
        from gui.worker import ContinuousVoiceWorker
        worker = ContinuousVoiceWorker()
        self.assertTrue(worker.running)
        worker.stop()
        self.assertFalse(worker.running)

    @patch('gui.main_window.ContinuousVoiceWorker')
    def test_gui_toggle_wake_mode_toggles_correctly(self, mock_worker_class):
        """16. Verify MainWindow toggle_wake_mode sets button state and spawns exactly one worker thread."""
        from gui.main_window import MainWindow
        from PyQt5.QtWidgets import QApplication
        
        # Standard QApplication singleton wrapper for GUI component instantiations in testing
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
            
        win = MainWindow()
        mock_worker = MagicMock()
        mock_worker.isRunning.return_value = False
        mock_worker_class.return_value = mock_worker
        
        # Verify initial button text
        self.assertEqual(win.wake_btn.text(), "Start Wake Mode")
        self.assertIsNone(win.continuous_voice_worker)
        
        # Toggle start
        win.toggle_wake_mode()
        self.assertEqual(win.wake_btn.text(), "Stop Wake Mode")
        mock_worker.start.assert_called_once()
        self.assertIsNotNone(win.continuous_voice_worker)
        
        # Toggle stop
        mock_worker.isRunning.return_value = True
        win.toggle_wake_mode()
        self.assertEqual(win.wake_btn.text(), "Start Wake Mode")
        mock_worker.stop.assert_called_once()
        self.assertIsNone(win.continuous_voice_worker)

    def test_clean_query(self):
        """17. Verify that clean_query strips wake word prefixes and leading punctuation correctly."""
        from gui.worker import ContinuousVoiceWorker
        worker = ContinuousVoiceWorker()
        
        # Test prefixes
        self.assertEqual(worker.clean_query("Nova what is the time"), "what is the time")
        self.assertEqual(worker.clean_query("Hey Nova date today"), "date today")
        self.assertEqual(worker.clean_query("ok nova read my screen"), "read my screen")
        self.assertEqual(worker.clean_query("okay nova, status"), "status")
        
        # Test case-insensitivity
        self.assertEqual(worker.clean_query("hEy NoVa, date today"), "date today")
        self.assertEqual(worker.clean_query("OKAY NOVA read my screen"), "read my screen")
        
        # Test direct mode (no prefix)
        self.assertEqual(worker.clean_query("what is the time right now"), "what is the time right now")
        
        # Test empty or none
        self.assertEqual(worker.clean_query(""), "")
        self.assertEqual(worker.clean_query(None), "")

    def test_setup_tesseract_configures_cmd(self):
        """18. Verify setup_tesseract sets tesseract_cmd path from config."""
        from automation.screen_reader import setup_tesseract
        import pytesseract
        old_val = config.TESSERACT_CMD
        try:
            config.TESSERACT_CMD = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
            setup_tesseract()
            self.assertEqual(pytesseract.pytesseract.tesseract_cmd, 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe')
        finally:
            config.TESSERACT_CMD = old_val

    def test_extract_text_missing_path_returns_error(self):
        """19. Verify extract_text_from_screen returns clear error message if TESSERACT_CMD is empty."""
        from automation.screen_reader import extract_text_from_screen
        old_val = config.TESSERACT_CMD
        try:
            config.TESSERACT_CMD = ''
            res = extract_text_from_screen()
            self.assertFalse(res["success"])
            self.assertIn("Screen reading failed: Tesseract OCR was not found", res["error"])
        finally:
            config.TESSERACT_CMD = old_val

    def test_extract_text_nonexistent_path_returns_error(self):
        """20. Verify extract_text_from_screen returns clear error if TESSERACT_CMD path does not exist."""
        from automation.screen_reader import extract_text_from_screen
        old_val = config.TESSERACT_CMD
        try:
            config.TESSERACT_CMD = 'C:\\nonexistent\\tesseract.exe'
            res = extract_text_from_screen()
            self.assertFalse(res["success"])
            self.assertIn("Screen reading failed: Tesseract OCR was not found", res["error"])
        finally:
            config.TESSERACT_CMD = old_val

    @patch('automation.screen_reader.os.path.exists')
    @patch('automation.screen_reader.Image.open')
    @patch('pytesseract.image_to_string')
    def test_extract_text_tesseract_not_found_error_caught(self, mock_image_to_string, mock_image_open, mock_exists):
        """21. Verify extract_text_from_screen catches TesseractNotFoundError and returns user-facing message."""
        import pytesseract
        from automation.screen_reader import extract_text_from_screen
        
        mock_exists.return_value = True
        mock_image_open.return_value = MagicMock()
        mock_image_to_string.side_effect = pytesseract.TesseractNotFoundError()
        
        old_val = config.TESSERACT_CMD
        try:
            config.TESSERACT_CMD = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
            res = extract_text_from_screen()
            self.assertFalse(res["success"])
            self.assertIn("Screen reading failed: Tesseract OCR was not found", res["error"])
        finally:
            config.TESSERACT_CMD = old_val

    @patch('automation.screen_reader.os.path.exists')
    @patch('automation.screen_reader.capture_screen')
    @patch('automation.screen_reader.Image.open')
    @patch('pytesseract.image_to_string')
    @patch('config.has_llm_credentials')
    @patch('core.tts.speak')
    def test_read_screen_response_cached_in_router(self, mock_speak, mock_has_llm, mock_image_to_string, mock_image_open, mock_capture, mock_exists):
        """22. Verify read_screen command populates router.get_last_response response cache."""
        from core.router import handle_command, get_last_response
        
        mock_exists.return_value = True
        mock_capture.return_value = {"success": True, "path": "dummy.png"}
        mock_image_open.return_value = MagicMock()
        mock_image_to_string.return_value = "Hello World"
        mock_has_llm.return_value = False
        
        old_val = config.TESSERACT_CMD
        try:
            config.TESSERACT_CMD = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
            success = handle_command("read screen", test_mode_active=True)
            self.assertTrue(success)
            
            last_resp = get_last_response()
            self.assertEqual(last_resp["response"], "I detected 1 lines of text (11 characters). Visible content includes: Hello World...")
        finally:
            config.TESSERACT_CMD = old_val

if __name__ == "__main__":
    unittest.main()
