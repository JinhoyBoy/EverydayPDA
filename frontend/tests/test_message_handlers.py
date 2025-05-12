import os
import sys

import unittest
import datetime
from unittest.mock import patch, MagicMock, AsyncMock, mock_open, ANY

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from message_handlers import MessageHandlers


class TestMessageHandlers(unittest.IsolatedAsyncioTestCase):
    @patch("message_handlers.api_client.get_all_morning_messages")
    @patch("message_handlers.speech_utils.generate_voice_message")
    @patch("message_handlers.open", new_callable=mock_open, read_data=b"FAKE AUDIO")
    async def test_send_morning_message_success(
        self,
        mock_file_open,
        mock_generate_voice,
        mock_get_morning
    ):
        # API liefert zwei Einträge zurück
        mock_get_morning.return_value = [
            {"response": "Guten Morgen!", "user_id": 111},
            {"response": "Hallo Tag!", "user_id": 222}
        ]
        mock_generate_voice.return_value = "/fake/path/to/audio.ogg"

        mh = MessageHandlers()
        context = AsyncMock()
        await mh.send_morning_message(context)

        # 1) Wir erwarten zwei Nachrichten + zwei Sprachnachrichten
        self.assertEqual(context.bot.send_message.call_count, 2)
        context.bot.send_message.assert_any_call(chat_id=111, text="Guten Morgen!")
        context.bot.send_message.assert_any_call(chat_id=222, text="Hallo Tag!")

        self.assertEqual(context.bot.send_voice.call_count, 2)
        context.bot.send_voice.assert_any_call(chat_id=111, voice=ANY)
        context.bot.send_voice.assert_any_call(chat_id=222, voice=ANY)

    @patch("message_handlers.api_client.get_all_morning_messages")
    @patch("message_handlers.logging.Logger.warning")
    async def test_send_morning_message_error_string(self, mock_logger, mock_api):
        # API gibt einen Fehler-String statt einer Liste zurück
        mock_api.return_value = "Fehler: 404"

        mh = MessageHandlers()
        context = AsyncMock()
        await mh.send_morning_message(context)

        # Keine Send-Calls, stattdessen Warnung geloggt
        context.bot.send_message.assert_not_called()
        context.bot.send_voice.assert_not_called()
        mock_logger.assert_called_once_with(
            "Fehler beim Abrufen der Morgenmeldungen: Fehler: 404"
        )

    @patch("message_handlers.api_client.get_all_proactivity_messages")
    @patch("message_handlers.speech_utils.generate_voice_message")
    @patch("message_handlers.open", new_callable=mock_open, read_data=b"FAKE AUDIO")
    async def test_send_proactivity_message_success(
        self,
        mock_file_open,
        mock_generate_voice,
        mock_get_proactivity
    ):
        mock_get_proactivity.return_value = [
            {"response": "Proaktive Info 1", "user_id": 333},
            {"response": "Proaktive Info 2", "user_id": 444}
        ]
        mock_generate_voice.return_value = "/fake/path/to/audio.ogg"

        mh = MessageHandlers()
        context = AsyncMock()
        await mh.send_proactivity_message(context)

        self.assertEqual(context.bot.send_message.call_count, 2)
        context.bot.send_message.assert_any_call(chat_id=333, text="Proaktive Info 1")
        context.bot.send_message.assert_any_call(chat_id=444, text="Proaktive Info 2")

        self.assertEqual(context.bot.send_voice.call_count, 2)

    @patch("message_handlers.api_client.get_all_proactivity_messages")
    @patch("message_handlers.logging.Logger.warning")
    async def test_send_proactivity_message_error_string(self, mock_logger, mock_api):
        mock_api.return_value = "Fehler: 500"

        mh = MessageHandlers()
        context = AsyncMock()
        await mh.send_proactivity_message(context)

        context.bot.send_message.assert_not_called()
        context.bot.send_voice.assert_not_called()
        mock_logger.assert_called_once_with(
            "Fehler beim Abrufen der Proaktivitätsmeldungen: Fehler: 500"
        )

    @patch("message_handlers.api_client.get_answer")
    @patch("message_handlers.speech_utils.generate_voice_message")
    @patch("message_handlers.open", new_callable=mock_open, read_data=b"FAKE AUDIO")
    async def test_handle_incoming_message_text(
        self,
        mock_file_open,
        mock_gen_voice,
        mock_get_answer
    ):
        mock_get_answer.return_value = "Antwort auf Textnachricht"
        mock_gen_voice.return_value = "/fake/path/out.ogg"

        mh = MessageHandlers()
        update = AsyncMock()
        context = AsyncMock()

        # Wir simulieren eine Textnachricht
        update.message.voice = None
        update.message.text = "Hallo Bot!"
        update.effective_user.id = 12345

        await mh.handle_incoming_message(update, context)

        mock_get_answer.assert_called_once_with("Hallo Bot!", 12345)
        context.bot.send_message.assert_not_called()  # die Antwort geht als reply_text
        update.message.reply_text.assert_called_once_with("Antwort auf Textnachricht")
        update.message.reply_voice.assert_called_once()

    @patch("message_handlers.api_client.get_answer")
    @patch("message_handlers.speech_utils.convert_voice_to_text")
    @patch("message_handlers.speech_utils.generate_voice_message")
    @patch("message_handlers.open", new_callable=mock_open, read_data=b"FAKE AUDIO")
    async def test_handle_incoming_message_voice(
        self,
        mock_file_open,
        mock_gen_voice,
        mock_conv_voice,
        mock_get_answer
    ):
        mock_conv_voice.return_value = "Gesprochener Text"
        mock_get_answer.return_value = "Antwort auf Sprache"
        mock_gen_voice.return_value = "/fake/path/out.ogg"

        mh = MessageHandlers()
        update = AsyncMock()
        context = AsyncMock()

        # Wir simulieren eine Voice-Nachricht
        update.message.voice = AsyncMock()
        update.effective_user.id = 55555

        # Der Download in handle_incoming_message
        mock_file = AsyncMock()
        update.message.voice.get_file.return_value = mock_file

        await mh.handle_incoming_message(update, context)
        mock_file.download_to_drive.assert_awaited()  # Voice-Datei wurde heruntergeladen
        mock_conv_voice.assert_called_once_with(
            mh.BASE_DIR + "/output.ogg"
        )
        mock_get_answer.assert_called_once_with("Gesprochener Text", 55555)
        update.message.reply_text.assert_called_once_with("Antwort auf Sprache")
        update.message.reply_voice.assert_called_once()

    @patch("message_handlers.datetime")
    def test_configure_proactivity_jobs(self, mock_datetime):
        # mock datetime.time, falls dein Code dynamische Zeitzugriffe hat
        mock_datetime.time.return_value = datetime.time(hour=21, minute=19, second=0)

        mh = MessageHandlers()
        application = MagicMock()

        mh.configure_proactivity_jobs(application)

        # Prüfen, dass run_daily & run_repeating korrekt aufgerufen wurden
        application.job_queue.run_daily.assert_called_once_with(
            mh.send_morning_message,
            time=mock_datetime.time.return_value,
            name="morning_message"
        )
        application.job_queue.run_repeating.assert_called_once_with(
            mh.send_proactivity_message,
            interval=600,
            first=0,
            name="proactivity_message"
        )


if __name__ == "__main__":
    unittest.main()