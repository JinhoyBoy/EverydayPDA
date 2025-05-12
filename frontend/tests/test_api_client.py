import os
import sys

import unittest
from unittest.mock import patch, Mock
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_client import (
    get_answer,
    get_all_morning_messages,
    get_all_proactivity_messages,
    get_preferences,
    post_preferences,
    put_preference,
)


class TestAPIClient(unittest.TestCase):
    @patch("requests.get")
    def test_get_answer_success(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"response": "Testantwort"}
        mock_get.return_value = mock_resp

        result = get_answer("Hallo", 123)
        self.assertEqual(result, "Testantwort")
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_get_answer_failure(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 400
        mock_get.return_value = mock_resp

        result = get_answer("Hallo", 123)
        self.assertIn("400: Fehler", result)

    @patch("requests.get", side_effect=requests.RequestException)
    def test_get_answer_exception(self, mock_get):
        result = get_answer("Hallo", 123)
        self.assertIn("nicht mit der API verbinden", result)

    @patch("requests.get")
    def test_get_all_morning_messages_success(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": ["msg1", "msg2"]}
        mock_get.return_value = mock_resp

        result = get_all_morning_messages()
        self.assertEqual(["msg1", "msg2"], result)

    @patch("requests.get")
    def test_get_all_morning_messages_failure(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        result = get_all_morning_messages()
        self.assertIn("404: Fehler", result)

    @patch("requests.get", side_effect=requests.RequestException)
    def test_get_all_morning_messages_exception(self, mock_get):
        result = get_all_morning_messages()
        self.assertIn("nicht mit der API verbinden", result)

    @patch("requests.get")
    def test_get_all_proactivity_messages_success(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": ["pmsg1"]}
        mock_get.return_value = mock_resp

        result = get_all_proactivity_messages()
        self.assertEqual(["pmsg1"], result)

    @patch("requests.get")
    def test_get_all_proactivity_messages_failure(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp

        result = get_all_proactivity_messages()
        self.assertIn("500: Fehler", result)

    @patch("requests.get", side_effect=requests.RequestException)
    def test_get_all_proactivity_messages_exception(self, mock_get):
        result = get_all_proactivity_messages()
        self.assertIn("nicht mit der API verbinden", result)

    @patch("requests.get")
    def test_get_preferences_success(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"course": "IN22"}
        mock_get.return_value = mock_resp

        prefs, status = get_preferences(999)
        self.assertEqual(status, "success")
        self.assertEqual(prefs, {"course": "IN22"})

    @patch("requests.get")
    def test_get_preferences_failure(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        prefs, status = get_preferences(999)
        self.assertEqual(status, "error")
        self.assertIn("404: Fehler", prefs)

    @patch("requests.get", side_effect=requests.RequestException)
    def test_get_preferences_exception(self, mock_get):
        prefs, status = get_preferences(999)
        self.assertEqual(status, "error")
        self.assertIn("nicht abrufen", prefs)

    @patch("requests.post")
    def test_post_preferences_success(self, mock_post):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        result = post_preferences(999, {"canteen": "Mensa", "stocks": ["ABC"]})
        self.assertIn("erfolgreich gespeichert", result)

    @patch("requests.post")
    def test_post_preferences_failure(self, mock_post):
        mock_resp = Mock()
        mock_resp.status_code = 400
        mock_post.return_value = mock_resp

        result = post_preferences(999, {})
        self.assertIn("400: Fehler", result)

    @patch("requests.post", side_effect=requests.RequestException)
    def test_post_preferences_exception(self, mock_post):
        result = post_preferences(999, {})
        self.assertIn("schon initialisiert", result)

    @patch("requests.put")
    @patch("requests.get")
    def test_put_preference_success(self, mock_get, mock_put):
        mock_get_resp = Mock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {"course": "IN22"}
        mock_get.return_value = mock_get_resp

        mock_put_resp = Mock()
        mock_put_resp.status_code = 200
        mock_put.return_value = mock_put_resp

        result = put_preference(999, "course", "IN23")
        self.assertIn("erfolgreich aktualisiert", result)

    @patch("requests.put")
    @patch("requests.get")
    def test_put_preference_invalid_key(self, mock_get, mock_put):
        mock_get_resp = Mock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {"course": "IN22"}
        mock_get.return_value = mock_get_resp

        result = put_preference(999, "invalid_key", "some_value")
        self.assertIn("Ungültige Präferenz", result)
        mock_put.assert_not_called()

    @patch("requests.put")
    @patch("requests.get")
    def test_put_preference_failure(self, mock_get, mock_put):
        mock_get_resp = Mock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {"course": "IN22"}
        mock_get.return_value = mock_get_resp

        mock_put_resp = Mock()
        mock_put_resp.status_code = 400
        mock_put.return_value = mock_put_resp

        result = put_preference(999, "course", "IN23")
        self.assertIn("Fehler bei der Aktualisierung: 400", result)

    @patch("requests.get", side_effect=requests.RequestException)
    def test_put_preference_get_exception(self, mock_get):
        result = put_preference(999, "course", "IN23")
        self.assertIn("nicht ändern", result)


if __name__ == "__main__":
    unittest.main()
