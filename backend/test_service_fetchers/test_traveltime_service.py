import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.service_fetchers.traveltime_service import get_travel_info

class TestGetTravelInfo(unittest.TestCase):

    @patch('backend.service_fetchers.traveltime_service.requests.post')
    @patch('backend.service_fetchers.traveltime_service.Nominatim.geocode')
    def test_get_travel_info_success(self, mock_geocode, mock_post):
        # Mock geocode return values
        mock_geocode.side_effect = [
            MagicMock(longitude=9.1829, latitude=48.7758),  # Stuttgart
            MagicMock(longitude=10.0000, latitude=53.5500)  # Hamburg
        ]

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "features": [{
                "properties": {
                    "segments": [{
                        "distance": 635000.0,
                        "duration": 23000.0
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        result = get_travel_info(["driving-car"], ["Stuttgart"], ["Hamburg"])

        expected = {
            "distance_km": 635.0,
            "duration_min": 383.33
        }

        self.assertEqual(result, expected)

    @patch('backend.service_fetchers.traveltime_service.Nominatim.geocode')
    def test_get_travel_info_invalid_location(self, mock_geocode):
        mock_geocode.return_value = None

        result = get_travel_info(["driving-car"], ["InvalidCity"], ["Hamburg"])
        self.assertEqual(result, {"error": "Ungültiger Start- oder Zielort"})

    @patch('backend.service_fetchers.traveltime_service.requests.post')
    @patch('backend.service_fetchers.traveltime_service.Nominatim.geocode')
    def test_get_travel_info_api_error(self, mock_geocode, mock_post):
        mock_geocode.side_effect = [
            MagicMock(longitude=9.1829, latitude=48.7758),
            MagicMock(longitude=10.0000, latitude=53.5500)
        ]

        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "API key invalid"}
        mock_post.return_value = mock_response

        result = get_travel_info(["driving-car"], ["Stuttgart"], ["Hamburg"])
        self.assertEqual(result, {"error": "API key invalid"})

if __name__ == '__main__':
    unittest.main()
