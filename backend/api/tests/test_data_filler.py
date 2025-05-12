import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from api.data_filler import DataFiller  # Passe den Importpfad ggf. an

class TestDataFiller(unittest.IsolatedAsyncioTestCase):

    @patch('api.data_filler.get_db_connection')  # Passe den Pfad zum Modul an
    async def test_fill_missing_values_fetch_from_database_and_defaults(self, mock_get_db_connection):
        # Mock DB-Verbindung und .fetch-Methode
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [('AAPL',), ('TSLA',)]
        mock_get_db_connection.return_value = mock_conn

        # Input-Daten mit gemischten Fällen
        data = {
            'Stock-Name': '',
            'News-Topic': [''],
            'City': '',
            'Destination-Location': '',
            'Destination-Airport': '',
            'InvalidKey': '',
        }

        expected_data = {
            'Stock-Name': ['AAPL', 'TSLA'],
            'News-Topic': ['AAPL', 'TSLA'],  # gleicher Rückgabewert für den Test, weil fetch() gleich gemockt
            'City': ['AAPL', 'TSLA'],
            'Destination-Location': 'DHBW Stuttgart',
            'Destination-Airport': 'Maldives',
            'InvalidKey': None,
        }

        df = DataFiller()
        result = await df.fill_missing_values(data.copy(), user_id='user123')

        self.assertEqual(result, expected_data)
        self.assertEqual(mock_conn.fetch.call_count, 3)
        mock_conn.close.assert_awaited()

    async def test_fill_missing_values_no_fetch_or_default(self):
        df = DataFiller()
        data = {
            'CompletelyUnknownKey': '',
        }
        result = await df.fill_missing_values(data.copy(), user_id='user123')
        self.assertEqual(result, {'CompletelyUnknownKey': None})

    def test_get_default_value(self):
        self.assertEqual(DataFiller._DataFiller__get_default_value('Destination-Location'), 'DHBW Stuttgart')
        self.assertIsNone(DataFiller._DataFiller__get_default_value('UnknownKey'))

    @patch('api.data_filler.get_db_connection')
    async def test_fetch_from_database_invalid_key(self, mock_get_db_connection):
        result = await DataFiller._DataFiller__fetch_from_database('InvalidKey', 'user123')
        self.assertIsNone(result)
        mock_get_db_connection.assert_not_called()

    @patch('api.data_filler.get_db_connection')
    async def test_fetch_from_database_no_result(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = []
        mock_get_db_connection.return_value = mock_conn

        result = await DataFiller._DataFiller__fetch_from_database('City', 'user123')
        self.assertIsNone(result)
        mock_conn.close.assert_awaited()

    @patch('api.data_filler.get_db_connection')
    async def test_fetch_from_database_single_result(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [ ["Berlin"]]
        mock_get_db_connection.return_value = mock_conn

        result = await DataFiller._DataFiller__fetch_from_database('City', 'user123')
        self.assertEqual(result, ['Berlin'])

if __name__ == '__main__':
    unittest.main()
