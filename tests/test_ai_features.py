import unittest
import os
import json
from unittest.mock import patch, MagicMock
import importlib # Added importlib

# Assuming the app structure is such that these imports work relative to the project root
from app.ai import (
    _load_prompts, SYSTEM_INSTRUCTION, COMMAND_PROMPTS, 
    SETUP_PROMPT_TEMPLATE, CHARACTER_CREATION_PROMPTS,
    call_gemini_api, GeminiAPIError,
    _get_token_count, manage_chat_history, MAX_CONTEXT_TOKENS, TOKEN_BUFFER
)
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
import google.generativeai as genai
import google.generativeai.protos as protos # Changed from genai_types
import app.ai # Import the module itself for reloading
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable


# Define a dummy prompts.json content for testing purposes
TEST_PROMPTS_CONTENT = {
    "system_instruction": "Test system instruction.",
    "command_prompts": {
        "test_command": "This is a test prompt for {param}.",
        "another_command": "Another test prompt."
    },
    "setup_prompt_template": "Setup for {game}, {players}.",
    "character_creation_prompts": {
        "base": "Base char prompt for {name}.",
        "acknowledgement": "Acknowledged {character}."
    }
}

class TestAIFeatures(unittest.TestCase):

    @patch('app.ai.json.load', return_value=TEST_PROMPTS_CONTENT)
    def test_load_prompts(self, mock_json_load):
        importlib.reload(app.ai) # Ensure globals are re-evaluated
        self.assertEqual(app.ai.SYSTEM_INSTRUCTION, TEST_PROMPTS_CONTENT["system_instruction"])
        self.assertEqual(app.ai.COMMAND_PROMPTS, TEST_PROMPTS_CONTENT["command_prompts"])
        self.assertEqual(app.ai.SETUP_PROMPT_TEMPLATE, TEST_PROMPTS_CONTENT["setup_prompt_template"])
        # Restore original state of globals
        importlib.reload(app.ai)

    @patch('app.ai.genai.GenerativeModel')
    def test_get_token_count(self, mock_generative_model):
        mock_model_instance = mock_generative_model.return_value
        mock_model_instance.count_tokens.return_value.total_tokens = 10
        
        mock_message1 = MagicMock(spec=protos.Content) # Changed from genai_types.Message
        mock_message1.parts = [MagicMock(text="Hello")]
        mock_message1.role = "user"
        mock_message2 = MagicMock(spec=protos.Content) # Changed from genai_types.Message
        mock_message2.parts = [MagicMock(text="Hi there")]
        mock_message2.role = "model"

        messages = [mock_message1, mock_message2]
        token_count = _get_token_count(mock_model_instance, messages)
        self.assertEqual(token_count, 10)
        mock_model_instance.count_tokens.assert_called_once()
    
    @patch('app.ai._get_token_count')
    @patch('app.ai.MAX_CONTEXT_TOKENS', 100) # Patch the constant directly for testing
    @patch('app.ai.TOKEN_BUFFER', 10)       # Patch the constant directly for testing
    def test_manage_chat_history_truncation(self, mock_get_token_count):
        mock_model = MagicMock(spec=genai.GenerativeModel)
        # Ensure model.count_tokens returns a mock object with an integer total_tokens
        mock_model.count_tokens.return_value = MagicMock(total_tokens=5) 

        mock_chat = MagicMock()
        mock_chat.history = [
            MagicMock(spec=protos.Content, parts=[MagicMock(text="Old message 1")], role="user"),
            MagicMock(spec=protos.Content, parts=[MagicMock(text="Old response 1")], role="model"),
            MagicMock(spec=protos.Content, parts=[MagicMock(text="Old message 2")], role="user"),
            MagicMock(spec=protos.Content, parts=[MagicMock(text="Old response 2")], role="model"),
        ]
        
        # Simulate history being too long
        # Let's say each message is 5 tokens, so history is 20 tokens.
        # MAX_CONTEXT_TOKENS = 100, TOKEN_BUFFER = 10 (as patched above)
        # If we return a value that makes total_tokens > MAX_CONTEXT_TOKENS
        
        # Test case 1: History needs truncation
        mock_get_token_count.side_effect = [
            70, # Initial history is 70 tokens (70 + 5 + 10 = 85, > 100)
            30, # After removing a pair, it's 30 tokens (30 + 5 + 10 = 45, < 100)
            # This needs to be refined. The mock_get_token_count is called multiple times.
            # 1. For current_history_tokens (initially 70)
            # 2. For recalculating current_history_tokens inside the loop (initially 70 - 2 messages*some tokens)
            # The new_message_tokens is only counted once for the incoming message.
            # Let's simplify the side_effect for clarity.
            # Assume each message pair is 20 tokens (10 user + 10 model)

            # First call for initial history token count
            MAX_CONTEXT_TOKENS - 2*20 - TOKEN_BUFFER + 1, # Initial history tokens + new_msg_tokens + buffer > MAX_CONTEXT_TOKENS
                                                          # 100 - 40 - 10 + 1 = 51 (initial history token count)
            # Second call after first truncation
            MAX_CONTEXT_TOKENS - 1*20 - TOKEN_BUFFER - 1, # History tokens after 1 truncation (100 - 20 - 10 - 1 = 69)
        ]
        
        new_message_content = "New user message"
        manage_chat_history(mock_model, mock_chat, new_message_content) # Pass mock_model
        
        self.assertEqual(len(mock_chat.history), 2) # One pair should be removed
        self.assertEqual(mock_chat.history[0].parts[0].text, "Old message 2")

        # Test case 2: History is already short enough
        mock_chat.history = [
            MagicMock(spec=protos.Content, parts=[MagicMock(text="Msg A")], role="user"),
            MagicMock(spec=protos.Content, parts=[MagicMock(text="Resp A")], role="model"),
        ]
        mock_get_token_count.side_effect = [
            MAX_CONTEXT_TOKENS - 2*20 - TOKEN_BUFFER - 100, # Initial history tokens + new_msg_tokens + buffer < MAX_CONTEXT_TOKENS
                                                            # 100 - 40 - 10 - 100 = -50 (initial history token count)
        ]
        manage_chat_history(mock_model, mock_chat, new_message_content) # Pass mock_model
        self.assertEqual(len(mock_chat.history), 2) # Should remain unchanged

    @patch('app.ai.manage_chat_history')
    @patch('app.ai.time.sleep') # To prevent actual sleep during retries
    def test_call_gemini_api_with_chat_send_message(self, mock_sleep, mock_manage_chat_history):
        mock_chat_instance = MagicMock() # No spec needed if we manually set attributes
        mock_chat_instance.model = MagicMock(spec=genai.GenerativeModel)
        mock_chat_instance.send_message = MagicMock(return_value=MagicMock(text="AI response", candidates=[MagicMock()]))
        # Need to ensure api_call_func.__self__ is our mock_chat_instance
        mock_chat_instance.send_message.__self__ = mock_chat_instance

        response = call_gemini_api(mock_chat_instance.send_message, "User message")
        
        mock_manage_chat_history.assert_called_once_with(mock_chat_instance.model, mock_chat_instance, "User message")
        mock_chat_instance.send_message.assert_called_once_with("User message")
        self.assertEqual(response.text, "AI response")

    @patch('app.ai.manage_chat_history')
    @patch('app.ai.time.sleep')
    def test_call_gemini_api_retry_on_resource_exhausted(self, mock_sleep, mock_manage_chat_history):
        mock_chat_instance = MagicMock()
        mock_chat_instance.model = MagicMock(spec=genai.GenerativeModel)
        
        # Simulate ResourceExhausted twice, then success
        mock_chat_instance.send_message = MagicMock(side_effect=[
            ResourceExhausted("Rate limit exceeded"),
            ResourceExhausted("Rate limit exceeded again"),
            MagicMock(text="AI response after retry", candidates=[MagicMock()])
        ])
        mock_chat_instance.send_message.__self__ = mock_chat_instance

        response = call_gemini_api(mock_chat_instance.send_message, "User message")
        
        self.assertEqual(mock_chat_instance.send_message.call_count, 3)
        self.assertIn("AI response after retry", response.text)

    @patch('app.ai.manage_chat_history')
    @patch('app.ai.time.sleep')
    def test_call_gemini_api_raises_gemini_api_error_on_no_candidates(self, mock_sleep, mock_manage_chat_history):
        mock_chat_instance = MagicMock()
        mock_chat_instance.model = MagicMock(spec=genai.GenerativeModel)
        mock_chat_instance.send_message = MagicMock(return_value=MagicMock(candidates=[])) # No candidates
        mock_chat_instance.send_message.__self__ = mock_chat_instance

        with self.assertRaises(GeminiAPIError) as cm:
            call_gemini_api(mock_chat_instance.send_message, "User message")
        self.assertIn("returned no candidates", str(cm.exception))

    @patch('app.ai.manage_chat_history')
    @patch('app.ai.time.sleep')
    def test_call_gemini_api_reraises_non_retryable_exception(self, mock_sleep, mock_manage_chat_history):
        mock_chat_instance = MagicMock()
        mock_chat_instance.model = MagicMock(spec=genai.GenerativeModel)
        
        # Simulate an unexpected, non-retryable exception
        mock_chat_instance.send_message = MagicMock(side_effect=ValueError("Non-retryable error"))
        mock_chat_instance.send_message.__self__ = mock_chat_instance

        with self.assertRaises(GeminiAPIError) as cm: # Changed to GeminiAPIError
            call_gemini_api(mock_chat_instance.send_message, "User message")
        self.assertIn("Non-retryable error", str(cm.exception))

if __name__ == '__main__':
    unittest.main()