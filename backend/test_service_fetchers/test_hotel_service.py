import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.service_fetchers.hotel_service import get_hotels

class TestGetHotels(unittest.TestCase):

    @patch('backend.service_fetchers.hotel_service.requests.get')
    @patch('backend.service_fetchers.hotel_service.is_valid_date')
    def test_get_hotels_success(self, mock_date, mock_get):
        mock_date.side_effect = ["2025-05-10", "2025-05-12"]

        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = [
            {
                "hotelName": "Hotel Berlin",
                "priceFrom": 120.0,
                "stars": 4
            },
            {
                "hotelName": "City Stay",
                "priceFrom": 95.5,
                "stars": 3
            }
        ]

        result = get_hotels(["Berlin"], ["10.05.2025"], ["12.05.2025"])

        expected = {
            "Hotel Berlin": {"price": 120.0, "stars": 4},
            "City Stay": {"price": 95.5, "stars": 3}
        }

        self.assertEqual(result, expected)

    @patch('backend.service_fetchers.hotel_service.requests.get')
    @patch('backend.service_fetchers.hotel_service.is_valid_date')
    def test_get_hotels_error_response(self, mock_date, mock_get):
        mock_date.side_effect = ["2025-05-10", "2025-05-12"]

        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = {"errorCode": 2}

        result = get_hotels(["Berlin"], ["10.05.2025"], ["12.05.2025"])

        self.assertEqual(result, {})

    @patch('backend.service_fetchers.hotel_service.requests.get')
    @patch('backend.service_fetchers.hotel_service.is_valid_date')
    def test_get_hotels_missing_fields(self, mock_date, mock_get):
        mock_date.side_effect = ["2025-05-10", "2025-05-12"]

        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = [
            {
                "hotelName": "Unknown Hotel"
                # priceFrom und stars fehlen
            }
        ]

        result = get_hotels(["Berlin"], ["10.05.2025"], ["12.05.2025"])

        expected = {
            "Unknown Hotel": {"price": "keine Angabe", "stars": "keine Angabe"}
        }

        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
