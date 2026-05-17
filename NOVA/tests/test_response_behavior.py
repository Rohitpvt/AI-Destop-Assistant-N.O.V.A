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

    @patch('core.tts.speak')
    def test_gui_worker_uses_get_last_response_for_chat(self, mock_speak):
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

if __name__ == "__main__":
    unittest.main()
