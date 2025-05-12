import os
import sys

import unittest
from unittest.mock import patch, MagicMock

# Wir nehmen an, dein Modul heißt einfach "bot".
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bot import BotApp

class TestBotApp(unittest.TestCase):
    @patch("bot.Application")
    def test_bot_app_run(self, mock_application_cls):
        # Application simulieren
        mock_builder = MagicMock()
        mock_app_instance = MagicMock()
        mock_application_cls.builder.return_value = mock_builder
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app_instance

        # BotApp anlegen
        bot_app = BotApp(token="TEST_TOKEN")

        # run() aufrufen
        bot_app.run()

        # Sicherstellen, dass run_polling auf der Application aufgerufen wurde
        mock_app_instance.run_polling.assert_called_once()


if __name__ == "__main__":
    unittest.main()