import os
import logging
import datetime
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CallbackContext,
    Application
)

import speech_utils
import api_client


class MessageHandlers:
    """
    Handles incoming messages and schedules daily messages (morning and proactivity).
    """

    def __init__(self):
        """
        Initialize the logger and set BASE_DIR for file operations.
        You can define BASE_DIR in the constructor as well.
        """
        self.logger = logging.getLogger(__name__)
        self.BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    async def send_morning_message(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Sends the daily morning message via the JobQueue.
        """
        response = api_client.get_all_morning_messages()

        if isinstance(response, str):
            self.logger.warning(f"Fehler beim Abrufen der Morgenmeldungen: {response}")
            return

        for item in response:
            text = item["response"]
            user_id = item["user_id"]

            if text is None:
                self.logger.warning(f"Keine Morgenmeldung für Benutzer {user_id} gefunden.")
                continue

            voice_output_path = speech_utils.generate_voice_message(text)
            await context.bot.send_message(chat_id=user_id, text=text)
            await context.bot.send_voice(chat_id=user_id, voice=open(voice_output_path, "rb"))

    async def send_proactivity_message(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Sends the daily proactivity message via the JobQueue.
        """
        response = api_client.get_all_proactivity_messages()

        if isinstance(response, str):
            self.logger.warning(f"Fehler beim Abrufen der Proaktivitätsmeldungen: {response}")
            return

        for item in response:
            text = item["response"]
            user_id = item["user_id"]

            if text is None:
                self.logger.warning(f"Keine Proaktivitätsmeldung für Benutzer {user_id} gefunden.")
                continue

            voice_output_path = speech_utils.generate_voice_message(text)
            await context.bot.send_message(chat_id=user_id, text=text)
            await context.bot.send_voice(chat_id=user_id, voice=open(voice_output_path, "rb"))

    async def handle_incoming_message(self, update: Update, context: CallbackContext):
        """
        Processes voice and text messages and returns an answer.
        """
        if update.message.voice:
            voice_path = os.path.join(self.BASE_DIR, "output.ogg")
            voice_file = await update.message.voice.get_file()
            await voice_file.download_to_drive(voice_path)

            input_text = speech_utils.convert_voice_to_text(voice_path)
            text = api_client.get_answer(input_text, update.effective_user.id)
        else:
            text = api_client.get_answer(update.message.text, update.effective_user.id)

        voice_output_path = speech_utils.generate_voice_message(text)
        await update.message.reply_text(text)
        await update.message.reply_voice(voice=open(voice_output_path, "rb"))

    def configure_proactivity_jobs(self, application: Application):
        """
        Sets up the recurring jobs for morning and proactivity messages.
        """
        morning_time = datetime.time(hour=7, minute=0, second=0) # UTC-Time
        proactivity_interval = 600  # seconds

        application.job_queue.run_daily(
            self.send_morning_message,
            time=morning_time,
            name="morning_message"
        )
        application.job_queue.run_repeating(
            self.send_proactivity_message,
            interval=proactivity_interval,
            first=0,
            name="proactivity_message"
        )

