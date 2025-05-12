import unittest
from unittest.mock import AsyncMock, patch
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from api.answer_processor import AnswerProcessor


class TestAnswerProcessor(unittest.IsolatedAsyncioTestCase):

    @patch('api.answer_processor.UseCaseHandler')
    async def test_get_answer(self, MockUseCaseHandler):
        mock_handler = MockUseCaseHandler.return_value
        mock_handler.get_use_cases_and_info = AsyncMock(return_value=(["uc1"], {"key": "value"}))
        mock_handler.call_apis.return_value = {"api": "data"}
        mock_handler.get_response.return_value = "final response"

        processor = AnswerProcessor()
        result = await processor.get_answer("Hello", "user123")

        self.assertEqual(result, {"response": "final response"})
        mock_handler.get_use_cases_and_info.assert_awaited_once_with("Hello", "user123")
        mock_handler.call_apis.assert_called_once_with(["uc1"], {"key": "value"})
        mock_handler.get_response.assert_called_once_with("Hello", {"api": "data"})

    @patch('api.answer_processor.get_all_users')
    @patch('api.answer_processor.UserSummaryGenerator')
    async def test_get_morning(self, MockUserSummaryGenerator, mock_get_all_users):
        mock_get_all_users.return_value = [{"username": "user1"}, {"username": "user2"}]
        mock_generator = MockUserSummaryGenerator.return_value
        mock_generator.get_user_morning = AsyncMock(side_effect=[
            {"response": "Good morning, user1!"},
            Exception("Failed to get morning summary")
        ])

        processor = AnswerProcessor()
        result = await processor.get_morning()

        expected = {
            "results": [
                {"user_id": "user1", "response": "Good morning, user1!"},
                {"user_id": "user2", "response": "Error: Failed to get morning summary"}
            ]
        }

        self.assertEqual(result, expected)

    @patch('api.answer_processor.get_all_users')
    @patch('api.answer_processor.UserSummaryGenerator')
    async def test_get_proactivity(self, MockUserSummaryGenerator, mock_get_all_users):
        mock_get_all_users.return_value = [{"username": "user1"}, {"username": "user2"}]
        mock_generator = MockUserSummaryGenerator.return_value
        mock_generator.get_user_proactivity = AsyncMock(side_effect=[
            {"response": "User1 is proactive!"},
            Exception("Something went wrong")
        ])

        processor = AnswerProcessor()
        result = await processor.get_proactivity()

        self.assertEqual(result["results"][0]["user_id"], "user1")
        self.assertEqual(result["results"][0]["response"], "User1 is proactive!")
        self.assertEqual(result["results"][1]["user_id"], "user2")
        self.assertTrue("Error: Something went wrong" in result["results"][1]["response"])
        self.assertTrue("Traceback:" in result["results"][1]["response"])


if __name__ == '__main__':
    unittest.main()
