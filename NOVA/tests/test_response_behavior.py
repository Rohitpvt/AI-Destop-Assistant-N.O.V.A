import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import datetime

# Add the parent directory and NOVA directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.router import handle_command
from memory import memory_db
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
    def test_time_command_returns_actual_time(self, mock_speak):
        """1. Verify that 'what is the time right now' returns the actual formatted time."""
        # Execute time command
        success = handle_command("what is the time right now", test_mode_active=True, takecommand_func=lambda: "exit")
        
        # Verify execution succeeded
        self.assertTrue(success)
        
        # Check saved interaction
        interactions = memory_db.get_recent_interactions(1)
        self.assertTrue(len(interactions) > 0)
        
        timestamp, cmd, resp, intent = interactions[0]
        self.assertEqual(cmd, "what is the time right now")
        self.assertEqual(intent, "time")
        
        # Verify format matches "The current time is HH:MM AM/PM."
        self.assertTrue(resp.startswith("The current time is "))
        self.assertTrue(resp.endswith(" AM.") or resp.endswith(" PM."))
        
    @patch('core.tts.speak')
    def test_date_command_returns_actual_date(self, mock_speak):
        """2. Verify that 'what is the date today' returns the actual formatted date."""
        # Execute date command
        success = handle_command("what is the date today", test_mode_active=True, takecommand_func=lambda: "exit")
        
        # Verify execution succeeded
        self.assertTrue(success)
        
        # Check saved interaction
        interactions = memory_db.get_recent_interactions(1)
        self.assertTrue(len(interactions) > 0)
        
        timestamp, cmd, resp, intent = interactions[0]
        self.assertEqual(cmd, "what is the date today")
        self.assertEqual(intent, "date")
        
        # Verify format matches "Today is Day, DD Month YYYY."
        self.assertTrue(resp.startswith("Today is "))
        now = datetime.datetime.now()
        year_str = str(now.year)
        self.assertTrue(resp.endswith(year_str + "."))
        
    @patch('core.tts.speak')
    @patch('ai.llm_client.call_llm')
    def test_generic_ai_question_uses_fallback(self, mock_call_llm, mock_speak):
        """3. Verify that a generic AI question falls back to call_llm using config key."""
        # Mock LLM to return a success response
        mock_call_llm.return_value = "Machine learning is a subset of artificial intelligence."
        
        # Mock LLM credentials to True
        with patch('config.has_llm_credentials', return_value=True), \
             patch('config.LLM_ENABLED', True):
            
            success = handle_command("explain machine learning in simple words", test_mode_active=True, takecommand_func=lambda: "exit")
            
            # Verify execution succeeded
            self.assertTrue(success)
            
            # Verify that call_llm was indeed invoked
            self.assertTrue(mock_call_llm.called)
            
            # Check database stores the correct response
            interactions = memory_db.get_recent_interactions(1)
            self.assertTrue(len(interactions) > 0)
            
            timestamp, cmd, resp, intent = interactions[0]
            self.assertEqual(cmd, "explain machine learning in simple words")
            self.assertEqual(intent, "general_chat")
            self.assertEqual(resp, "Machine learning is a subset of artificial intelligence.")
            
    @patch('core.tts.speak')
    def test_gui_displays_user_response_instead_of_log(self, mock_speak):
        """4. Verify that GUI CommandWorker extracts the user_response (resp) instead of log_message."""
        # Trigger time command which writes the user friendly time to DB
        handle_command("what is the time right now", test_mode_active=True, takecommand_func=lambda: "exit")
        
        # Simulate CommandWorker response retrieval:
        interactions = memory_db.get_recent_interactions(1)
        self.assertTrue(len(interactions) > 0)
        
        resp = interactions[0][2]
        
        # Assert resp does NOT contain developer logs like "Told the time."
        self.assertNotEqual(resp, "Told the time.")
        self.assertTrue(resp.startswith("The current time is "))
        
    @patch('core.tts.speak')
    def test_memory_stores_user_response_instead_of_log(self, mock_speak):
        """5. Verify that sqlite memory stores the actual user_response (resp) instead of log_message."""
        # Trigger date command which writes the user friendly date to DB
        handle_command("what is the date today", test_mode_active=True, takecommand_func=lambda: "exit")
        
        # Query the raw database row directly to verify storage integrity
        conn = memory_db.get_connection()
        self.assertIsNotNone(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT user_command, nova_response, intent FROM interactions ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        user_cmd, nova_resp, intent = row
        
        self.assertEqual(user_cmd, "what is the date today")
        self.assertEqual(intent, "date")
        
        # Assert stored response does NOT contain developer logs like "Told the date."
        self.assertNotEqual(nova_resp, "Told the date.")
        self.assertTrue(nova_resp.startswith("Today is "))

if __name__ == "__main__":
    unittest.main()
