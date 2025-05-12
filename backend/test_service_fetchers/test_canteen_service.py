import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.service_fetchers.canteen_service import get_canteen_info

class TestGetCanteenInfo(unittest.TestCase):

    @patch('requests.get')
    def test_get_canteen_info_success(self, mock_get):
        mock_get.side_effect = [
            # Canteen list page 1
            MagicMock(status_code=200, json=MagicMock(return_value=[
                {"id": 42, "name": "Mensa Central", "city": "Stuttgart"}
            ])),
            # Canteen list page 2 (empty to end paging)
            MagicMock(status_code=200, json=MagicMock(return_value=[])),
            # Meals API response
            MagicMock(status_code=200, json=MagicMock(return_value=[
                {"name": "Spaghetti Bolognese", "category": "Main dish", "prices": {"students": 2.5}},
                {"name": "Gemüsepfanne", "category": "Vegetarian", "prices": {"students": 2.0}},
                {"name": "Suppe", "category": "Starter", "prices": {"students": 1.5}}
            ]))
        ]

        result = get_canteen_info(["Mensa Central"])
        expected = {
            "Mensa Central": {
                "Spaghetti Bolognese": {"category": "Main dish", "price": 2.5},
                "Gemüsepfanne": {"category": "Vegetarian", "price": 2.0},
                "Suppe": {"category": "Starter", "price": 1.5}
            }
        }

        self.assertEqual(result, expected)

    @patch('requests.get')
    def test_get_canteen_info_not_found(self, mock_get):
        mock_get.side_effect = [
            MagicMock(status_code=200, json=MagicMock(return_value=[
                {"id": 42, "name": "Andere Mensa", "city": "Stuttgart"}
            ])),
            MagicMock(status_code=200, json=MagicMock(return_value=[]))
        ]

        result = get_canteen_info(["Nicht Existente Mensa"])
        expected = {"Nicht Existente Mensa": {"error": "Kantine nicht gefunden."}}
        self.assertEqual(result, expected)

    @patch('requests.get')
    def test_get_canteen_info_api_failure(self, mock_get):
        mock_get.return_value = MagicMock(status_code=404)
        result = get_canteen_info(["Mensa Central"])
        expected = {"error": "Fehler beim Laden der Kantinen: 404"}
        self.assertEqual(result, expected)

    @patch('requests.get')
    def test_get_canteen_info_meal_api_failure(self, mock_get):
        mock_get.side_effect = [
            # Canteen list page 1
            MagicMock(status_code=200, json=MagicMock(return_value=[
                {"id": 1, "name": "Mensa Central", "city": "Stuttgart"}
            ])),
            # Canteen list page 2
            MagicMock(status_code=200, json=MagicMock(return_value=[])),
            # Meals API returns error
            MagicMock(status_code=404)
        ]

        result = get_canteen_info(["Mensa Central"])
        expected = {"Mensa Central": {"error": "Fehler beim Abrufen: 404"}}
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
