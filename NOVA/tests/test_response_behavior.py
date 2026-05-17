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

if __name__ == "__main__":
    unittest.main()
