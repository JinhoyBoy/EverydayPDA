import unittest
from unittest.mock import patch, MagicMock
import ast

import UseCaseProcessor as ucp_module
from UseCaseProcessor import UseCaseProcessor, UseCaseSelection, ExtractedInformation
from llm_fetchers.ChatGPTProcessor import ChatGPTProcessor

# Dummy UseCase to simulate available APIs (mimicking UseCases)
class DummyUseCase:
    def __init__(self, value, description):
        self.value = value
        self.description = description

# Dummy classes to simulate the response structure from OpenAI
class DummyMessage:
    def __init__(self, content, parsed=None):
        self.content = content
        self.parsed = parsed

class DummyChoice:
    def __init__(self, message):
        self.message = message

class DummyResponse:
    def __init__(self, choices):
        self.choices = choices

class TestUseCaseProcessor(unittest.TestCase):
    def setUp(self):
        # Reset the singleton instance in ChatGPTProcessor used by UseCaseProcessor
        ChatGPTProcessor._instance = None

    def test_parse_response_failure(self):
        processor = UseCaseProcessor()
        invalid_literals = [
            "not a valid literal",
            "123abc",        
            "{'key': 'value'", 
        ]
        for invalid in invalid_literals:
            with self.subTest(invalid=invalid):
                result = processor.parse_response(invalid)
                # Expect the invalid input to be returned unmodified.
                self.assertEqual(result, invalid)

    @patch("llm_fetchers.ChatGPTProcessor.OpenAI")
    def test_declare_usecase_success(self, mock_openai):
        # Create dummy use cases to simulate UseCases
        dummy_use_cases = [
            DummyUseCase(1, "API 1"),
            DummyUseCase(2, "API 2"),
            DummyUseCase(3, "API 3")
        ]
        # Patch the module-level UseCases in UseCaseProcessor to our dummy list
        with patch.dict(ucp_module.__dict__, {"UseCases": dummy_use_cases}):
            # Build a dummy parsed response with use_case_ids attribute
            DummyParsed = type("DummyParsed", (), {})()
            DummyParsed.use_case_ids = "[1,2]"
            dummy_message = DummyMessage(content="", parsed=DummyParsed)
            dummy_choice = DummyChoice(dummy_message)
            dummy_response = DummyResponse([dummy_choice])
            # Setup the mock client chain for process_input_with_context
            mock_client = MagicMock()
            mock_client.beta = MagicMock()
            mock_client.beta.chat = MagicMock()
            mock_client.beta.chat.completions = MagicMock()
            mock_client.beta.chat.completions.parse.return_value = dummy_response
            mock_openai.return_value = mock_client

            processor = UseCaseProcessor()
            result = processor.declare_usecase("Test input")
            # Filtering available API IDs [1,2,3] should yield [1,2]
            self.assertEqual(result, [1, 2])

    @patch("llm_fetchers.ChatGPTProcessor.OpenAI")
    def test_get_information_success(self, mock_openai):
        # Create dummy information dictionary
        dummy_info = {'Stocks': ['IBM'], 'News Services': ['CNN']}
        # Build a dummy parsed response with info attribute
        DummyParsed = type("DummyInfo", (), {})()
        DummyParsed.info = str(dummy_info)
        dummy_message = DummyMessage(content="", parsed=DummyParsed)
        dummy_choice = DummyChoice(dummy_message)
        dummy_response = DummyResponse([dummy_choice])
        # Setup the mock client chain for process_input_with_context
        mock_client = MagicMock()
        mock_client.beta = MagicMock()
        mock_client.beta.chat = MagicMock()
        mock_client.beta.chat.completions = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = dummy_response
        mock_openai.return_value = mock_client

        processor = UseCaseProcessor()
        result = processor.get_information("Test input", "Stocks, News Services")
        self.assertEqual(result, dummy_info)

    @patch("llm_fetchers.ChatGPTProcessor.OpenAI")
    def test_response_success(self, mock_openai):
        # Create a dummy text response for process_input
        dummy_message = DummyMessage("Response text")
        dummy_choice = DummyChoice(dummy_message)
        dummy_response = DummyResponse([dummy_choice])
        # Setup the mock chain for process_input
        mock_client = MagicMock()
        mock_client.beta = MagicMock()
        mock_client.beta.chat = MagicMock()
        mock_client.beta.chat.completions = MagicMock()
        mock_client.beta.chat.completions.parse.return_value = dummy_response
        mock_openai.return_value = mock_client

        processor = UseCaseProcessor()
        result = processor.response("User input", "API call data")
        self.assertEqual(result, "Response text")

if __name__ == "__main__":
    unittest.main()