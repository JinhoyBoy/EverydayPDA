import os
import sys

import unittest
from unittest.mock import patch, AsyncMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pref_handler import PreferenceHandler


class TestPreferenceHandler(unittest.IsolatedAsyncioTestCase):
    @patch("pref_handler.api_client.get_preferences")
    async def test_get_summary_success(self, mock_get_preferences):
        mock_get_preferences.return_value = (
            {
                "course": "Informatik",
                "cafeteria": "Mensa A",
                "city": "Berlin",
                "preferred_transport_medium": "Bus",
                "stocks": ["Apple", "Tesla"],
                "news": ["Politik", "Sport"],
            },
            "success",
        )

        handler = PreferenceHandler()
        update = AsyncMock()
        context = AsyncMock()

        summary = await handler.get_summary(update, context)

        self.assertIn("Hier ist deine Übersicht:", summary)
        self.assertIn("📚 Kurs: Informatik", summary)
        self.assertIn("🍽️ Mensa: Mensa A", summary)
        self.assertIn("🏠 Wohnort: Berlin", summary)
        self.assertIn("🚆 Transport: Bus", summary)
        self.assertIn("📈 Lieblingsaktien: Apple, Tesla", summary)
        self.assertIn("📰 Nachrichtenquellen: Politik, Sport", summary)

    @patch("pref_handler.api_client.get_preferences")
    async def test_get_summary_no_preferences(self, mock_get_preferences):
        mock_get_preferences.return_value = (None, "error")

        handler = PreferenceHandler()
        update = AsyncMock()
        context = AsyncMock()

        summary = await handler.get_summary(update, context)

        self.assertEqual(
            summary,
            "Du hast noch keine Präferenzen festgelegt. Starte den Einrichtungsprozess mit /start.",
        )

    @patch("pref_handler.api_client.put_preference")
    async def test_change_canteen(self, mock_put_preference):
        mock_put_preference.return_value = "Mensa geändert!"

        handler = PreferenceHandler()
        update = AsyncMock()
        context = AsyncMock()

        update.message.text = "Neue Mensa"
        update.effective_user.id = 123

        next_state = await handler.change_canteen(update, context)

        mock_put_preference.assert_called_once_with(123, "cafeteria", "Neue Mensa")
        update.message.reply_text.assert_awaited_with("Mensa geändert!")
        self.assertEqual(next_state, -1) # ConversationHandler.END

    @patch("pref_handler.api_client.put_preference")
    async def test_change_city(self, mock_put_preference):
        mock_put_preference.return_value = "Wohnort geändert!"

        handler = PreferenceHandler()
        update = AsyncMock()
        context = AsyncMock()

        update.message.text = "Neue Stadt"
        update.effective_user.id = 456

        next_state = await handler.change_city(update, context)

        mock_put_preference.assert_called_once_with(456, "city", "Neue Stadt")
        update.message.reply_text.assert_awaited_with("Wohnort geändert!")
        self.assertEqual(next_state, -1) # ConversationHandler.END

    @patch("pref_handler.api_client.put_preference")
    async def test_add_stocks(self, mock_put_preference):
        mock_put_preference.return_value = "Aktien hinzugefügt!"

        handler = PreferenceHandler()
        update = AsyncMock()
        context = AsyncMock()

        update.message.text = "Apple, Tesla"
        update.effective_user.id = 789

        next_state = await handler.add_stocks(update, context)

        mock_put_preference.assert_called_once_with(789, "add_stocks", ["Apple", "Tesla"])
        update.message.reply_text.assert_awaited_with("Aktien hinzugefügt!")
        self.assertEqual(next_state, -1) # ConversationHandler.END

    @patch("pref_handler.api_client.put_preference")
    async def test_remove_news(self, mock_put_preference):
        mock_put_preference.return_value = "Nachrichtenthemen entfernt!"

        handler = PreferenceHandler()
        update = AsyncMock()
        context = AsyncMock()

        update.message.text = "Politik, Sport"
        update.effective_user.id = 999

        next_state = await handler.remove_news(update, context)

        mock_put_preference.assert_called_once_with(999, "delete_news", ["Politik", "Sport"])
        update.message.reply_text.assert_awaited_with("Nachrichtenthemen entfernt!")
        self.assertEqual(next_state, -1) # ConversationHandler.END

    @patch("pref_handler.InlineKeyboardButton")
    @patch("pref_handler.InlineKeyboardMarkup")
    async def test_start_change_preferences(self, mock_markup_cls, mock_button_cls):
        handler = PreferenceHandler()
        update = AsyncMock()
        context = AsyncMock()

        await handler.start_change_preferences(update, context)

        update.message.reply_text.assert_awaited()
        mock_markup_cls.assert_called_once()
        mock_button_cls.assert_called()

    @patch("pref_handler.api_client.put_preference")
    async def test_process_preference_button_click(self, mock_put_preference):
        handler = PreferenceHandler()
        update = AsyncMock()
        context = AsyncMock()

        update.callback_query.data = "canteen"
        update.callback_query.answer = AsyncMock()

        next_state = await handler.process_preference_button_click(update, context)

        update.callback_query.answer.assert_awaited()
        update.callback_query.message.reply_text.assert_awaited_with(
            "Was ist deine neue Mensa?"
        )
        self.assertEqual(next_state, 6)  # CANTEEN_UPDATE


if __name__ == "__main__":
    unittest.main()