import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..')))
from backend.api.main import app

class TestGetPreferences(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)  

    @patch("api.database_utils.get_db_connection")
    async def test_get_preferences(self, mock_get_db_connection):
        
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.fetchrow.return_value = {
            "username": "testuser",
            "course": "Computer Science",
            "cafeteria": "Main Hall",
            "city": "Berlin",
            "preferred_transport_medium": "Bike",
            "stocks": "Apple,Google",
            "news": "CNN,BBC"
        }

        response = self.client.get("/preferences/testuser")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "username": "testuser",
            "course": "Computer Science",
            "cafeteria": "Main Hall",
            "city": "Berlin",
            "preferred_transport_medium": "Bike",
            "stocks": ["Apple", "Google"],
            "news": ["CNN", "BBC"]
        })

    @patch("api.database_utils.get_db_connection")
    async def test_get_preferences_user_not_found(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.fetchrow.return_value = None 

        response = self.client.get("/preferences/nonexistentuser")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User not found"})

# Definiere einen Dummy asynchronen Kontextmanager
class DummyTransaction:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        pass

class TestInitPreferences(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("api.database_utils.get_db_connection", new_callable=AsyncMock)
    async def test_init_preferences_success(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        # Hier ersetzen wir die transaction-Methode durch eine normale Funktion, 
        # die unseren DummyTransaction zurückgibt.
        mock_conn.transaction = lambda: DummyTransaction(mock_conn)
        mock_get_db_connection.return_value = mock_conn

        # Reihenfolge der fetchval-Aufrufe:
        # 1. COUNT(*) -> 0
        # 2. INSERT INTO users -> user_id 100
        # 3. Für "Apple": SELECT -> None, INSERT -> 200
        # 4. Für "Google": SELECT -> None, INSERT -> 201
        # 5. Für "CNN": SELECT -> None, INSERT -> 300
        # 6. Für "BBC": SELECT -> None, INSERT -> 301
        mock_conn.fetchval.side_effect = [0, 100, None, 200, 201, None, 300, 301]
        mock_conn.fetchrow.return_value = None

        user_data = {
            "username": "testuser",
            "course": "Computer Science",
            "cafeteria": "Main Hall",
            "city": "Berlin",
            "preferred_transport_medium": "Bike",
            "stocks": ["Apple", "Google"],
            "news": ["CNN", "BBC"]
        }

        response = self.client.post("/preferences/init", json=user_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "User created successfully", "user_id": 100})
        mock_conn.fetchval.assert_any_call("SELECT COUNT(*) FROM users WHERE username = $1", "testuser")

    @patch("api.database_utils.get_db_connection", new_callable=AsyncMock)
    async def test_init_preferences_user_already_exists(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        mock_conn.transaction = lambda: DummyTransaction(mock_conn)
        mock_get_db_connection.return_value = mock_conn

        # Bereits existierender User: fetchval liefert 1
        mock_conn.fetchval.side_effect = [1]

        user_data = {
            "username": "existinguser",
            "course": "Math",
            "cafeteria": "Main Hall",
            "city": "Berlin",
            "preferred_transport_medium": "Car",
            "stocks": ["Tesla"],
            "news": ["Reuters"]
        }

        response = self.client.post("/preferences/init", json=user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "User already exists"})
        
    @patch("api.database_utils.get_db_connection", new_callable=AsyncMock)
    async def test_init_preferences_with_existing_stocks_and_news(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        # Ersetze die transaction-Methode mit einer Lambda, die den Dummy-Transaktions-Kontextmanager zurückgibt
        mock_conn.transaction = lambda: DummyTransaction(mock_conn)
        mock_get_db_connection.return_value = mock_conn

        # Reihenfolge der Aufrufe:
        # 1. Überprüfen, ob der User existiert (0 = existiert nicht)
        # 2. Einfügen des Users und Rückgabe der u_id (43)
        # 3. Für "Amazon": SELECT -> 10 (existierender s_id)
        # 4. Für "Microsoft": SELECT -> 11
        # 5. Für "NYT": SELECT -> 20 (existierender n_id)
        # 6. Für "Guardian": SELECT -> 21
        mock_conn.fetchval.side_effect = [0, 43, 10, 11, 20, 21]

        user_data = {
            "username": "testuser2",
            "course": "Physics",
            "cafeteria": "Science Cafe",
            "city": "Hamburg",
            "preferred_transport_medium": "Train",
            "stocks": ["Amazon", "Microsoft"],
            "news": ["NYT", "Guardian"]
        }

        response = self.client.post("/preferences/init", json=user_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "User created successfully", "user_id": 43})

        mock_conn.fetchval.assert_any_call("SELECT s_id FROM stocks WHERE stock_name = $1", "Amazon")
        mock_conn.fetchval.assert_any_call("SELECT s_id FROM stocks WHERE stock_name = $1", "Microsoft")
        mock_conn.fetchval.assert_any_call("SELECT n_id FROM news WHERE news_name = $1", "NYT")
        mock_conn.fetchval.assert_any_call("SELECT n_id FROM news WHERE news_name = $1", "Guardian")


class TestUpdatePreferences(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("api.database_utils.get_db_connection", new_callable=AsyncMock)
    async def test_update_preferences_success(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        # Ersetze die transaction-Methode, damit der "async with"-Block korrekt funktioniert.
        mock_conn.transaction = lambda: DummyTransaction(mock_conn)
        mock_get_db_connection.return_value = mock_conn
        
        # Reihenfolge der Aufrufe:
        # 1. Gibt die Benutzer-ID zurück (user_id).
        # 2. Gibt None zurück (stock 1 existiert nicht).
        # 3. Gibt None zurück (stock 2 existiert nicht).
        # 4. Gibt eine ID für ein existierendes Stock zurück (stock 3).
        # 5. Gibt None zurück (news 1 existiert nicht).
        # 6. Gibt None zurück (news 2 existiert nicht).
        mock_conn.fetchval.side_effect = [1, None, None, 2, None, None]

        response = self.client.put(
            "/preferences/testuser",
            json={
                "course": "Mathematics",
                "cafeteria": "North Wing",
                "city": "Munich",
                "preferred_transport_medium": "Car",
                "add_stocks": ["Tesla"],
                "delete_stocks": ["Google"],
                "add_news": ["Reuters"],
                "delete_news": ["CNN"]
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "User preferences updated successfully"})
        
        # Prüfe, ob execute und fetchval aufgerufen wurden und die Verbindung geschlossen wurde
        mock_conn.execute.assert_called()
        mock_conn.fetchval.assert_called()
        mock_conn.close.assert_called()

    @patch("api.database_utils.get_db_connection", new_callable=AsyncMock)
    async def test_update_preferences_user_not_found(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        mock_conn.transaction = lambda: DummyTransaction(mock_conn)
        mock_get_db_connection.return_value = mock_conn
        
        mock_conn.fetchval.return_value = None 
        
        response = self.client.put(
            "/preferences/unknownuser",
            json={
                "course": "Physics"
            }
        )
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User not found"})
        mock_conn.close.assert_called()

if __name__ == "__main__":
    unittest.main()
