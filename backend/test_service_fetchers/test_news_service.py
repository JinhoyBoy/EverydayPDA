import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.service_fetchers.news_service import get_news

class TestGetNews(unittest.TestCase):

    @patch('backend.service_fetchers.news_service.requests.get')
    def test_get_news_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "totalResults": 1,
            "articles": [{
                "title": "Tech Innovation 2025",
                "url": "https://example.com/tech-innovation",
                "publishedAt": "2025-04-10T10:00:00Z"
            }]
        }
        mock_get.return_value = mock_response

        result = get_news(["technology"])

        expected = {
            "technology": [{
                "title": "Tech Innovation 2025",
                "source": "https://example.com/tech-innovation",
                "publishedAt": "2025-04-10T10:00:00Z"
            }]
        }

        self.assertEqual(result, expected)

    @patch('backend.service_fetchers.news_service.requests.get')
    def test_get_news_no_articles(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "totalResults": 0,
            "articles": []
        }
        mock_get.return_value = mock_response

        result = get_news(["sports"])
        self.assertEqual(result, {})

    @patch('backend.service_fetchers.news_service.requests.get')
    def test_get_news_missing_fields(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "totalResults": 1,
            "articles": [{}]  # Alle Felder fehlen
        }
        mock_get.return_value = mock_response

        result = get_news(["health"])

        expected = {
            "health": [{
                "title": None,
                "source": None,
                "publishedAt": None
            }]
        }

        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
