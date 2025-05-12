import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.service_fetchers.flight_service import get_flights

class TestGetFlights(unittest.TestCase):

    @patch('backend.service_fetchers.flight_service.requests.get')
    @patch('backend.service_fetchers.flight_service.requests.post')
    @patch('backend.service_fetchers.flight_service.is_valid_date', side_effect=lambda x: "2025-04-20")
    def test_get_flights_success(self, mock_date, mock_post, mock_get):
        # Mock OAuth token
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {"access_token": "fake_token"}

        # Mock IATA code lookup and flight offers
        def side_effect_get(url, headers=None, params=None):
            if "locations" in url:
                return MagicMock(
                    status_code=200,
                    json=lambda: {"data": [{"iataCode": "BER"}]} if params["keyword"] == "Berlin" else {"data": [{"iataCode": "HAM"}]}
                )
            elif "flight-offers" in url:
                return MagicMock(
                    status_code=200,
                    json=lambda: {
                        "data": [{
                            "itineraries": [{
                                "segments": [{
                                    "carrierCode": "LH",
                                    "departure": {"at": "2025-04-20T08:00"},
                                    "arrival": {"at": "2025-04-20T09:30"}
                                }]
                            }],
                            "price": {"grandTotal": "120.00"}
                        }]
                    }
                )
        mock_get.side_effect = side_effect_get

        result = get_flights(["Berlin"], ["Hamburg"], ["20.04.2025"])

        expected = {
            "flights": [{
                "flight_number": "LH",
                "airline": "LH",
                "departure": "2025-04-20T08:00",
                "arrival": "2025-04-20T09:30",
                "price": "120.00"
            }]
        }

        self.assertEqual(result, expected)

    @patch('backend.service_fetchers.flight_service.requests.post')
    def test_get_flights_token_failure(self, mock_post):
        mock_post.side_effect = Exception("Token request failed")
        result = get_flights(["Berlin"], ["Hamburg"], ["20.04.2025"])
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Token request failed")

    @patch('backend.service_fetchers.flight_service.requests.post')
    @patch('backend.service_fetchers.flight_service.requests.get')
    def test_get_flights_no_iata_code(self, mock_get, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {"access_token": "fake_token"}
        mock_get.return_value = MagicMock(status_code=200)
        mock_get.return_value.json.return_value = {"data": []}
        result = get_flights(["UnknownCity"], ["Hamburg"], ["20.04.2025"])
        self.assertIn("error", result)
        self.assertIn("No IATA code found", result["error"])

    @patch('backend.service_fetchers.flight_service.requests.post')
    @patch('backend.service_fetchers.flight_service.requests.get')
    def test_get_flights_no_data(self, mock_get, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {"access_token": "fake_token"}
        
        def side_effect_get(url, headers=None, params=None):
            if "locations" in url:
                return MagicMock(status_code=200, json=lambda: {"data": [{"iataCode": "BER"}]})
            elif "flight-offers" in url:
                return MagicMock(status_code=200, json=lambda: {"data": []})
        mock_get.side_effect = side_effect_get

        result = get_flights(["Berlin"], ["Hamburg"], ["20.04.2025"])
        self.assertEqual(result, {"error": "No flight data available."})

if __name__ == '__main__':
    unittest.main()
