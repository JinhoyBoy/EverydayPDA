import os
import sys

import unittest
from unittest.mock import patch, AsyncMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from start_handler import StartHandler

class TestStartHandler(unittest.IsolatedAsyncioTestCase):
    @patch("start_handler.api_client")
    async def test_start_initialization(self, mock_api):
        """Testet start_initialization, ob User-Name und ID verarbeitet und korrekte Texte gesendet werden."""
        handler = StartHandler()
        update = AsyncMock()
        context = AsyncMock()

        # Simuliere User
        update.effective_user.first_name = "Alice"
        update.effective_user.id = 123

        # Aufruf
        next_state = await handler.start_initialization(update, context)
        # Prüfen, ob korrekte Texte gesendet wurden
        update.message.reply_text.assert_any_await(
            "Hallo Alice mit der User-ID: 123! Ich bin EverydayPDA, dein persönlicher Assistent! 🤖\nIch werde ein paar Fragen stellen, um dich besser kennenzulernen. 😊"
        )
        update.message.reply_text.assert_any_await("Wo ist deine Mensa (z. B. Mensa Central)?")
        # Wir erwarten, dass der State = CANTEEN ist (wird normalerweise aus pref_config importiert)
        # Falls du CANTEEN ebenfalls patchen möchtest:
        # @patch("start_handler.CANTEEN", 100)
        # NextState sollte "CANTEEN" sein
        self.assertEqual(next_state, 0)  # Oder "CANTEEN" – je nachdem welche Konstante in pref_config hinterlegt ist

    async def test_initialize_canteen(self):
        """Testet initialize_canteen, ob Text gespeichert und nächste Frage gesendet wird."""
        handler = StartHandler()
        update = AsyncMock()
        context = AsyncMock()

        update.effective_user.id = 123
        update.message.text = "Mensa Central"

        next_state = await handler.initialize_canteen(update, context)
        self.assertEqual(
            handler.user_data_store[123]["canteen"], 
            "Mensa Central"
        )
        update.message.reply_text.assert_awaited_with("Wo lebst du? (z. B. Berlin, München, etc.)")
        # Wir erwarten, dass next_state = CITY
        self.assertEqual(next_state, 1)  # Oder "CITY"

    async def test_initialize_city(self):
        """Testet initialize_city, wechselt direkt weiter zum Transport-Handler."""
        handler = StartHandler()
        update = AsyncMock()
        context = AsyncMock()

        update.effective_user.id = 444
        update.message.text = "Berlin"

        next_state = await handler.initialize_city(update, context)
        # "city" sollte in user_data_store stehen
        self.assertEqual(handler.user_data_store[444]["city"], "Berlin")
        # initialize_city ruft am Ende initialize_transport auf und gibt dessen State zurück
        self.assertEqual(next_state, 2)  # Oder "TRANSPORT"

    @patch("start_handler.InlineKeyboardButton")
    @patch("start_handler.InlineKeyboardMarkup")
    async def test_initialize_transport_message(
        self, mock_markup_cls, mock_button_cls
    ):
        """Testet initialize_transport, wenn eine Nachricht kommt (kein CallbackQuery)."""
        handler = StartHandler()
        update = AsyncMock()
        context = AsyncMock()

        # update.message != None => wir bauen eine Tastatur
        next_state = await handler.initialize_transport(update, context)
        mock_markup_cls.assert_called_once()  # Tastatur erstellt
        update.message.reply_text.assert_awaited()  # Bot schenkt dem User Tastatur
        # Wir erwarten TRANSPORT
        self.assertEqual(next_state, 2)  # Oder TRANSPORT

    async def test_initialize_transport_callback(self):
        """Test, dass man per CallbackQuery sein Transportmittel auswählt."""
        handler = StartHandler()
        update = AsyncMock()
        context = AsyncMock()

        update.message = None  # => wir haben einen Callback
        update.callback_query.data = "transport:Bus"
        update.callback_query.answer = AsyncMock()
        update.effective_user.id = 789

        next_state = await handler.initialize_transport(update, context)
        self.assertEqual(handler.user_data_store[789]["transport"], "Bus")
        update.callback_query.edit_message_text.assert_awaited_with(
            "Dein bevorzugtes Transportmittel: Bus"
        )
        update.callback_query.message.reply_text.assert_awaited_with(
            "Welche Lieblingsaktien hast du? (Kommagetrennt, z.B. Apple, Tesla)"
        )
        # Wir erwarten den nächsten State = STOCKS
        self.assertEqual(next_state, 3)

    async def test_initialize_stocks(self):
        """Testet initialize_stocks, ob Aktien-Liste korrekt gespeichert wird."""
        handler = StartHandler()
        update = AsyncMock()
        context = AsyncMock()
        update.effective_user.id = 999
        update.message.text = "Apple,  Tesla ,   Alphabet "

        next_state = await handler.initialize_stocks(update, context)
        self.assertEqual(handler.user_data_store[999]["stocks"], ["Apple", "Tesla", "Alphabet"])
        update.message.reply_text.assert_awaited()

        # Dann die konkreten Aufrufe untersuchen:
        calls = update.message.reply_text.await_args_list
        found_substring = False
        for call in calls:
            # Hol dir das erste Argument (text) aus args oder kwargs
            if call.args and "Wähle aus diesen Optionen:" in call.args[0]:
                found_substring = True
                break
        self.assertTrue(found_substring)
        # initialize_stocks ruft am Ende initialize_news auf und gibt dessen State zurück
        self.assertEqual(next_state, 4)  # NEWS

    @patch("start_handler.InlineKeyboardButton")
    @patch("start_handler.InlineKeyboardMarkup")
    async def test_initialize_news_message(self, mock_markup_cls, mock_button_cls):
        """Testet initialize_news, wenn eine normale Nachricht reinkommt (=Start)."""
        handler = StartHandler()
        update = AsyncMock()
        context = AsyncMock()

        update.message = AsyncMock()
        update.callback_query = None
        # user_data sollte empty sein => wir legen es an
        context.user_data = {}

        next_state = await handler.initialize_news(update, context)
        self.assertEqual(context.user_data["selected_news"], [])
        update.message.reply_text.assert_awaited()
        self.assertEqual(next_state, 4)  # NEWS

    @patch("start_handler.api_client.post_preferences", return_value="Daten gespeichert.")
    async def test_end_initialization_message(self, mock_post):
        """Testet end_initialization, wenn's per normaler Message aufgerufen wird."""
        handler = StartHandler()
        update = AsyncMock()
        context = AsyncMock()

        update.message = AsyncMock()
        update.effective_user.id = 42
        # user_data_store füllen
        handler.user_data_store[42] = {
            "canteen": "Mensa A",
            "city": "Hamburg",
            "transport": "Fahrrad",
            "stocks": ["Apple", "Tesla"],
            "news": ["Sport", "Politik"]
        }

        next_state = await handler.end_initialization(update, context)
        update.message.reply_text.assert_awaited_with("Klicke jederzeit auf das Menü, um die Präferenzen zu ändern.")
        self.assertEqual(next_state, -1)  # ConversationHandler.END

if __name__ == "__main__":
    unittest.main()