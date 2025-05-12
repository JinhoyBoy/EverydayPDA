import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.service_fetchers.stock_service import get_stock_price

class TestGetStockPrice(unittest.TestCase):

    @patch('backend.service_fetchers.stock_service.requests.get')
    def test_get_stock_price_success(self, mock_get):
        # Reihenfolge der Aufrufe: symbol_search, time_series, quote
        mock_get.side_effect = [
            # symbol_search
            MagicMock(json=lambda: {"data": [{"symbol": "AAPL"}]}),
            # time_series
            MagicMock(json=lambda: {
                "values": [{"close": "173.80", "datetime": "2024-04-10 16:00:00"}]
            }),
            # quote
            MagicMock(json=lambda: {"change": "+1.25"})
        ]

        result = get_stock_price(["Apple"])

        expected = {
            "Apple": {
                "price": "173.80",
                "timestamp": "2024-04-10 16:00:00",
                "changeFrom1hour": "+1.25"
            }
        }

        self.assertEqual(result, expected)

    @patch('backend.service_fetchers.stock_service.requests.get')
    def test_get_stock_price_no_data(self, mock_get):
        # Keine Daten bei symbol_search
        mock_get.return_value = MagicMock(json=lambda: {})

        result = get_stock_price(["InvalidCompany"])
        self.assertEqual(result, {})

    @patch('backend.service_fetchers.stock_service.requests.get')
    def test_get_stock_price_api_error(self, mock_get):
        # symbol_search → erfolgreich
        # time_series → erfolgreich
        # quote → Fehlercode
        mock_get.side_effect = [
            MagicMock(json=lambda: {"data": [{"symbol": "AAPL"}]}),
            MagicMock(json=lambda: {
                "values": [{"close": "173.80", "datetime": "2024-04-10 16:00:00"}]
            }),
            MagicMock(json=lambda: {"code": 400})
        ]

        result = get_stock_price(["Apple"])
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
