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

    def test_session_context_operations(self):
        """23. Verify session_context update, get, and clear operations."""
        from core import session_context
        session_context.clear_context()
        ctx = session_context.get_context()
        self.assertEqual(ctx["active_app"], "")
        
        session_context.update_context(active_app="Notepad", control_mode="safe")
        ctx2 = session_context.get_context()
        self.assertEqual(ctx2["active_app"], "Notepad")
        self.assertEqual(ctx2["control_mode"], "safe")
        
        session_context.clear_context()
        ctx3 = session_context.get_context()
        self.assertEqual(ctx3["active_app"], "")

    def test_pending_approval_set_clear_expiry(self):
        """24. Verify pending approval staging, clearing, and expiry rules."""
        from core import session_context
        session_context.clear_context()
        self.assertFalse(session_context.has_pending_approval())
        
        action = {"action": "click", "target": "Search", "arguments": {"x": 100, "y": 200}, "expires_after_seconds": 1}
        session_context.set_pending_approval(action)
        self.assertTrue(session_context.has_pending_approval())
        
        ctx = session_context.get_context()
        pending = ctx["pending_approval"]
        self.assertEqual(pending["action"], "click")
        self.assertEqual(pending["target"], "Search")
        
        # Test expiry
        import time
        time.sleep(1.1)
        from core import approval
        res = approval.execute_pending_action()
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Approval expired.")

    @patch('core.desktop_controller.get_active_window_title')
    @patch('core.desktop_controller.click_at')
    def test_active_window_mismatch_blocks_stale_click(self, mock_click_at, mock_get_title):
        """25. Verify active window mismatch blocks a stale scheduled click action."""
        from core import session_context, approval
        session_context.clear_context()
        
        mock_get_title.return_value = "Chrome"
        action = {"action": "click", "target": "Search", "arguments": {"x": 100, "y": 200}}
        session_context.set_pending_approval(action)
        
        # Change active window title
        mock_get_title.return_value = "Word"
        res = approval.execute_pending_action()
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Active window has changed unexpectedly.")
        mock_click_at.assert_not_called()

    @patch('webbrowser.open')
    def test_open_website_action_succeeds(self, mock_open):
        """26. Verify low-risk website launch executes directly without approval."""
        from core import desktop_controller
        res = desktop_controller.open_website("google.com")
        self.assertTrue(res["success"])
        mock_open.assert_called_once_with("https://google.com")

    def test_risky_actions_require_approval(self):
        """27. Verify risky click/type actions require approval and do not execute silently."""
        from core import desktop_controller, session_context
        session_context.clear_context()
        
        res = desktop_controller.click_at(100, 200)
        self.assertTrue(res.get("approval_pending"))
        self.assertIn("I'm ready to click", res["prompt"])
        
        res2 = desktop_controller.type_text("hello")
        self.assertTrue(res2.get("approval_pending"))
        self.assertIn("ready to type 'hello'", res2["prompt"])

    @patch('core.desktop_controller.get_active_window_title')
    @patch('core.desktop_controller.pyautogui.click')
    def test_confirm_executes_pending_action(self, mock_click, mock_get_title):
        """28. Verify confirm command executes staged action and cancel clears it."""
        from core import session_context, approval, router
        session_context.clear_context()
        
        mock_get_title.return_value = "Mocked Window Title"
        action = {"action": "click", "target": "Search", "arguments": {"x": 150, "y": 250}}
        session_context.set_pending_approval(action)
        
        # Execute confirm
        success = router.handle_command("confirm", test_mode_active=True)
        self.assertTrue(success)
        mock_click.assert_called_once_with(150, 250)
        self.assertFalse(session_context.has_pending_approval())
        
        # Test cancel
        action2 = {"action": "click", "target": "Search", "arguments": {"x": 150, "y": 250}}
        session_context.set_pending_approval(action2)
        success = router.handle_command("cancel", test_mode_active=True)
        self.assertTrue(success)
        self.assertFalse(session_context.has_pending_approval())

    def test_resolve_visible_target_scenarios(self):
        """29. Verify target coordinate resolution, partial/exact matching, and ambiguity handling."""
        from core import session_context, desktop_controller
        session_context.clear_context()
        
        # Scenario 1: Empty items
        resolved = desktop_controller.resolve_visible_target("Search")
        self.assertIsNone(resolved)
        
        # Populate visible items
        items = [
            {"text": "Search", "confidence": 90, "x": 10, "y": 20, "width": 50, "height": 10, "center_x": 35, "center_y": 25},
            {"text": "Search Google", "confidence": 80, "x": 100, "y": 200, "width": 80, "height": 20, "center_x": 140, "center_y": 210},
            {"text": "Submit Search", "confidence": 85, "x": 300, "y": 400, "width": 80, "height": 20, "center_x": 340, "center_y": 410}
        ]
        session_context.update_context(last_visible_items=items)
        
        # Scenario 2: Exact match
        resolved2 = desktop_controller.resolve_visible_target("Search")
        self.assertEqual(resolved2["text"], "Search")
        self.assertEqual(resolved2["center_x"], 35)
        
        # Scenario 3: Partial match
        resolved3 = desktop_controller.resolve_visible_target("Google")
        self.assertEqual(resolved3["text"], "Search Google")
        
        # Scenario 4: Ambiguous matches
        items_ambig = [
            {"text": "Search Google", "confidence": 80, "x": 100, "y": 200, "width": 80, "height": 20, "center_x": 140, "center_y": 210},
            {"text": "Submit Search", "confidence": 85, "x": 300, "y": 400, "width": 80, "height": 20, "center_x": 340, "center_y": 410}
        ]
        session_context.update_context(last_visible_items=items_ambig)
        resolved5 = desktop_controller.resolve_visible_target("Search")
        self.assertIsInstance(resolved5, str)
        self.assertIn("multiple matches", resolved5)

    @patch('core.desktop_controller.get_active_window_title')
    def test_click_it_pronoun_resolution(self, mock_get_title):
        """30. Verify click it uses last_target to resolve click action coordinates."""
        from core import session_context, router
        session_context.clear_context()
        mock_get_title.return_value = "Mocked Window Title"
        
        items = [{"text": "Login", "confidence": 90, "x": 10, "y": 20, "width": 50, "height": 10, "center_x": 35, "center_y": 25}]
        session_context.update_context(last_visible_items=items, last_target="Login")
        
        success = router.handle_command("click it", test_mode_active=True)
        self.assertTrue(success)
        self.assertTrue(session_context.has_pending_approval())
        self.assertEqual(session_context.get_context()["pending_approval"]["target"], "Login")

    def test_destructive_commands_blocked(self):
        """31. Verify destructive commands are rejected and blocked by the safety gate."""
        from core import approval
        
        bad_action = {
            "action": "type",
            "target": "",
            "arguments": {"text": "format c: /q"}
        }
        self.assertFalse(approval.is_action_allowed(bad_action))
        
        bad_action2 = {
            "action": "hotkey",
            "target": "",
            "arguments": {"keys": ["alt", "f4"]}
        }
        self.assertFalse(approval.is_action_allowed(bad_action2))
        
        bad_action3 = {
            "action": "press_key",
            "target": "shutdown the computer",
            "arguments": {"key": "enter"}
        }
        self.assertFalse(approval.is_action_allowed(bad_action3))

if __name__ == "__main__":
    unittest.main()
