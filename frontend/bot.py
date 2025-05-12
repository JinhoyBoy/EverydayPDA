"""Module for building and running the Telegram bot application."""

from telegram.ext import (
    Application,
    MessageHandler,
    filters,
)

from command_handlers import CommandHandlers
from message_handlers import MessageHandlers


class BotApp:
    """Main bot application class."""

    def __init__(self, token: str):
        """
        Initialize the bot application with the given token.
        """
        self.application = Application.builder().token(token).build()
        self.msg_handlers = MessageHandlers()
        self.cmd_handlers = CommandHandlers()
        self._configure_handlers()
        self._configure_jobs()

    def _configure_handlers(self):
        """
        Configure command handlers and a default message handler
        that listens for text or voice messages.
        """
        self.cmd_handlers.configure_conversation_handlers(self.application)
        message_filter = (filters.TEXT & ~filters.COMMAND) | filters.VOICE
        self.application.add_handler(
            MessageHandler(message_filter, self.msg_handlers.handle_incoming_message)
        )

    def _configure_jobs(self):
        """
        Configure scheduled jobs for morning and proactivity messages.
        """
        self.msg_handlers.configure_proactivity_jobs(self.application)

    def run(self):
        """
        Start the bot's polling loop.
        """
        self.application.run_polling()




