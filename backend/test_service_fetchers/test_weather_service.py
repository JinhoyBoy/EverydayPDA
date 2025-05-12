import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.service_fetchers.weather_service import get_weather

class TestGetWeather(unittest.TestCase):

    @patch('requests.get')
    def test_get_weather_success(self, mock_get):
        # Mocking the API response for a valid city (e.g., Berlin)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "current": {"temp_c": 15.5, "feelslike_c": 14.0},
            "forecast": {
                "forecastday": [{
                    "day": {"maxtemp_c": 18.0, "mintemp_c": 12.0}
                }]
            }
        }
        mock_get.return_value = mock_response
        
        cities = ["Berlin"]
        result = get_weather(cities)

        expected = {
            "Berlin": {
                "temperature": 15.5,
                "feelslike": 14.0,
                "max_temp": 18.0,
                "min_temp": 12.0
            }
        }

        self.assertEqual(result, expected)

    @patch('requests.get')
    def test_get_weather_no_matching_location(self, mock_get):
        # Mocking the API response for an invalid city (e.g., city not found)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {"message": "No matching location found."}
        }
        mock_get.return_value = mock_response

        cities = ["InvalidCity"]
        result = get_weather(cities)

        self.assertEqual(result, {})

    @patch('requests.get')
    def test_get_weather_partial_data(self, mock_get):
        # Mocking the API response for a city with missing data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "current": {"temp_c": 10.0, "feelslike_c": 8.0},
            "forecast": {
                "forecastday": [{
                    "day": {"maxtemp_c": 12.0}  # Missing min_temp
                }]
            }
        }
        mock_get.return_value = mock_response
        
        cities = ["Paris"]
        result = get_weather(cities)

        expected = {
            "Paris": {
                "temperature": 10.0,
                "feelslike": 8.0,
                "max_temp": 12.0,
                "min_temp": None  # Should be None because min_temp is missing in the response
            }
        }

        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
