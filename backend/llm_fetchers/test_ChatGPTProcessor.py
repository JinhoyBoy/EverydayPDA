import unittest
from unittest.mock import patch, MagicMock
from ChatGPTProcessor import ChatGPTProcessor

class TestChatGPTProcessor(unittest.TestCase):

    def setUp(self):
        ChatGPTProcessor._instance = None

    @patch("ChatGPTProcessor.OpenAI")
    def test_process_input_success(self, mock_openai):
        # Setup the mock client and its method chain for a successful response
        mock_client_instance = MagicMock()
        mock_openai.return_value = mock_client_instance

        # Create a dummy message object with content attribute
        dummy_message = MagicMock()
        dummy_message.content = "Test response"
        dummy_choice = MagicMock(message=dummy_message)
        dummy_response = MagicMock()
        dummy_response.choices = [dummy_choice]

        # Simulate the chain: beta.chat.completions.parse returning our dummy response
        mock_client_instance.beta = MagicMock()
        mock_client_instance.beta.chat = MagicMock()
        mock_client_instance.beta.chat.completions = MagicMock()
        mock_client_instance.beta.chat.completions.parse.return_value = dummy_response

        processor = ChatGPTProcessor()
        result = processor.process_input("Test message")
        self.assertEqual(result, "Test response")
        mock_client_instance.beta.chat.completions.parse.assert_called_once()

    @patch("ChatGPTProcessor.OpenAI")
    def test_process_input_error(self, mock_openai):
        # Setup the mock client and its method chain to throw an exception
        mock_client_instance = MagicMock()
        mock_openai.return_value = mock_client_instance
        mock_client_instance.beta = MagicMock()
        mock_client_instance.beta.chat = MagicMock()
        mock_client_instance.beta.chat.completions = MagicMock()
        mock_client_instance.beta.chat.completions.parse.side_effect = Exception("API error")
        processor = ChatGPTProcessor()
        with self.assertRaises(Exception) as context:
            processor.process_input("Test message")
        self.assertIn("Error processing input", str(context.exception))

if __name__ == "__main__":
    unittest.main()