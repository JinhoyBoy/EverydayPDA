import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from api.summary_generator import UserSummaryGenerator
from UseCases import UseCases


class TestUserSummaryGenerator(unittest.IsolatedAsyncioTestCase):

    @patch("api.summary_generator.DataFiller")
    @patch("api.summary_generator.UseCaseHandler")
    async def test_get_user_morning(self, mock_usecase_handler, mock_data_filler):
        mock_data_filler.return_value.fill_missing_values = AsyncMock(return_value={"some_info": "value"})
        mock_usecase_handler.return_value.call_apis = MagicMock(return_value={"api_data": "value"})
        mock_usecase_handler.return_value.get_response = MagicMock(return_value="Guten Morgen! ...")

        generator = UserSummaryGenerator()
        result = await generator.get_user_morning("user123")

        self.assertEqual(result["response"], "Guten Morgen! ...")

    @patch("api.summary_generator.DataFiller")
    @patch("api.summary_generator.UseCaseHandler")
    async def test_get_user_proactivity_with_significant_data(self, mock_usecase_handler, mock_data_filler):
        stocks = {
            "AAPL": {"changeFrom1hour": "2.5"},
            "TSLA": {"changeFrom1hour": "-1.1"}
        }
        news = {
            "some_news": [{
                "publishedAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }]
        }

        mock_data_filler.return_value.fill_missing_values = AsyncMock(return_value={"some_info": "value"})
        mock_usecase_handler.return_value.call_apis = MagicMock(return_value={
            UseCases.STOCKS.description: stocks,
            UseCases.NEWS.description: news
        })
        mock_usecase_handler.return_value.get_response = MagicMock(return_value="Hey, hast du schon gehört? ...")

        generator = UserSummaryGenerator()
        result = await generator.get_user_proactivity("user456")

        self.assertEqual(result["response"], "Hey, hast du schon gehört? ...")

    @patch("api.summary_generator.DataFiller")
    @patch("api.summary_generator.UseCaseHandler")
    async def test_get_user_proactivity_with_no_significant_data(self, mock_usecase_handler, mock_data_filler):
        stocks = {
            "AAPL": {"changeFrom1hour": "0.2"},
            "TSLA": {"changeFrom1hour": "0.5"}
        }
        news = {
            "some_news": [{
                "publishedAt": "2000-01-01T00:00:00Z"
            }]
        }

        mock_data_filler.return_value.fill_missing_values = AsyncMock(return_value={"some_info": "value"})
        mock_usecase_handler.return_value.call_apis = MagicMock(return_value={
            UseCases.STOCKS.description: stocks,
            UseCases.NEWS.description: news
        })

        generator = UserSummaryGenerator()
        result = await generator.get_user_proactivity("user789")

        self.assertIsNone(result["response"])


if __name__ == "__main__":
    unittest.main()
