from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext

from pref_config import (
    BUTTON, CANTEEN_UPDATE, CITY_UPDATE, TRANSPORT_UPDATE,
    STOCKS_DELETE, STOCKS_ADD, NEWS_DELETE, NEWS_ADD
)
import api_client


class PreferenceHandler:
    """
    Handles user preference setup and modification within the chatbot.
    """

    def __init__(self):
        """
        Initialize the PreferenceHandler instance (currently does nothing special).
        """
        pass

    async def ask_user_for_preference_change(
        self,
        update: Update,
        context: CallbackContext,
        state: int,
        message: str
    ) -> int:
        """
        Asks the user for a new entry for the preference.
        Keeps the message in German as requested.
        """
        query = update.callback_query
        await query.message.reply_text(message)
        return state

    async def get_summary(self, update: Update, context: CallbackContext) -> str:
        """
        Retrieves the user's preferences and returns a formatted summary in German.
        """
        prefs, status = api_client.get_preferences(update.effective_user.id)
        if status == "success":
            summary = (
                "Hier ist deine Übersicht:\n\n"
                f"📚 Kurs: {prefs['course']}\n"
                f"🍽️ Mensa: {prefs['cafeteria']}\n"
                f"🏠 Wohnort: {prefs['city']}\n"
                f"🚆 Transport: {prefs['preferred_transport_medium']}\n"
                f"📈 Lieblingsaktien: {', '.join(prefs['stocks'])}\n"
                f"📰 Nachrichtenquellen: {', '.join(prefs['news'])}"
            )
            return summary
        return (
            "Du hast noch keine Präferenzen festgelegt. "
            "Starte den Einrichtungsprozess mit /start."
        )

    async def show_preferences(self, update: Update, context: CallbackContext):
        """
        Shows the user's current preferences if available,
        or indicates none are set.
        """
        text = await self.get_summary(update, context)
        await update.message.reply_text(text)

    async def start_change_preferences(self, update: Update, context: CallbackContext):
        """
        Allows the user to view and change existing preferences.
        """
        text = await self.get_summary(update, context)
        await update.message.reply_text(text)
        keyboard = [
            [InlineKeyboardButton("🍽️ Mensa", callback_data="canteen")],
            [InlineKeyboardButton("🏠 Wohnort", callback_data="city")],
            [InlineKeyboardButton("🚆 Transport", callback_data="transport")],
            [InlineKeyboardButton("📈 Aktien", callback_data="stocks")],
            [InlineKeyboardButton("📰 Nachrichten", callback_data="news")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Welche Präferenz möchtest du ändern?:",
            reply_markup=reply_markup
        )
        return BUTTON

    async def change_canteen(self, update: Update, context: CallbackContext) -> int:
        """
        Updates the user's cafeteria preference with the text they provide.
        """
        new_canteen = update.message.text.strip()
        response = api_client.put_preference(
            update.effective_user.id, "cafeteria", new_canteen
        )
        await update.message.reply_text(response)
        return ConversationHandler.END

    async def change_city(self, update: Update, context: CallbackContext) -> int:
        """
        Updates the user's city preference.
        """
        new_residence = update.message.text.strip()
        response = api_client.put_preference(
            update.effective_user.id, "city", new_residence
        )
        await update.message.reply_text(response)
        return ConversationHandler.END

    async def change_transport(self, update: Update, context: CallbackContext) -> int:
        """
        Updates the user's transport preference.
        """
        new_transport = update.message.text.strip()
        response = api_client.put_preference(
            update.effective_user.id, "preferred_transport_medium", new_transport
        )
        await update.message.reply_text(response)
        return ConversationHandler.END

    async def remove_stocks(self, update: Update, context: CallbackContext) -> int:
        """
        Removes one or more stock items from the user's preferences.
        """
        stocks = [s.strip() for s in update.message.text.split(",")]
        response = api_client.put_preference(
            update.effective_user.id, "delete_stocks", stocks
        )
        await update.message.reply_text(response)
        return ConversationHandler.END

    async def add_stocks(self, update: Update, context: CallbackContext) -> int:
        """
        Adds one or more stock items to the user's preferences.
        """
        stocks = [s.strip() for s in update.message.text.split(",")]
        response = api_client.put_preference(
            update.effective_user.id, "add_stocks", stocks
        )
        await update.message.reply_text(response)
        return ConversationHandler.END

    async def remove_news(self, update: Update, context: CallbackContext) -> int:
        """
        Removes specified news topics from the user's preferences.
        """
        chosen_news = [n.strip() for n in update.message.text.split(",")]
        response = api_client.put_preference(
            update.effective_user.id, "delete_news", chosen_news
        )
        await update.message.reply_text(response)
        return ConversationHandler.END

    async def add_news(self, update: Update, context: CallbackContext) -> int:
        """
        Adds specified news topics to the user's preferences.
        """
        chosen_news = [n.strip() for n in update.message.text.split(",")]
        response = api_client.put_preference(
            update.effective_user.id, "add_news", chosen_news
        )
        await update.message.reply_text(response)
        return ConversationHandler.END

    async def process_preference_button_click(
        self,
        update: Update,
        context: CallbackContext
    ) -> int:
        """
        Handles button clicks for modifying user preferences.
        """
        query = update.callback_query
        await query.answer()

        if query.data == "canteen":
            return await self.ask_user_for_preference_change(
                update, context, CANTEEN_UPDATE, "Was ist deine neue Mensa?"
            )
        if query.data == "city":
            return await self.ask_user_for_preference_change(
                update, context, CITY_UPDATE, "Was ist dein neuer Wohnort?"
            )
        if query.data == "transport":
            return await self.ask_user_for_preference_change(
                update, context, TRANSPORT_UPDATE, "Was ist dein neuer Transport?"
            )
        if query.data == "stocks":
            keyboard = [
                [InlineKeyboardButton("Aktien löschen", callback_data="stocks_delete")],
                [InlineKeyboardButton("Aktien hinzufügen", callback_data="stocks_add")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                "Wähle eine Option aus:", reply_markup=reply_markup
            )
        elif query.data == "news":
            keyboard = [
                [InlineKeyboardButton("Nachrichtenthemen löschen", callback_data="news_delete")],
                [InlineKeyboardButton("Nachrichtenthemen hinzufügen", callback_data="news_add")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                "Wähle eine Option aus:", reply_markup=reply_markup
            )
        elif query.data == "stocks_delete":
            return await self.ask_user_for_preference_change(
                update,
                context,
                STOCKS_DELETE,
                "Welche Aktien möchtest du entfernen?"
            )
        elif query.data == "stocks_add":
            return await self.ask_user_for_preference_change(
                update,
                context,
                STOCKS_ADD,
                "Welche Aktien möchtest du hinzufügen?"
            )
        elif query.data == "news_delete":
            return await self.ask_user_for_preference_change(
                update,
                context,
                NEWS_DELETE,
                "Welche Nachrichtenthemen möchtest du entfernen?"
            )
        elif query.data == "news_add":
            return await self.ask_user_for_preference_change(
                update,
                context,
                NEWS_ADD,
                "Welche Nachrichtenthemen möchtest du hinzufügen?"
            )
        return ConversationHandler.END