import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

import api_client
from pref_config import (
    CANTEEN,
    CITY,
    TRANSPORT,
    STOCKS,
    NEWS,
    NEWS_CATEGORIES,
    TRANSPORT_CATEGORIES
)


class StartHandler:
    """
    Manages user initialization flow, gathering basic preferences.
    """

    def __init__(self):
        """
        Initializes a dictionary to store user data.
        """
        self.user_data_store = {}

    async def start_initialization(self, update: Update, context: CallbackContext):
        """
        Greets the user in German and asks for their cafeteria preference.
        """
        user_name = update.effective_user.first_name
        user_id = update.effective_user.id
        await update.message.reply_text(
            f"Hallo {user_name} mit der User-ID: {user_id}! Ich bin EverydayPDA, "
            "dein persönlicher Assistent! 🤖\n"
            "Ich werde ein paar Fragen stellen, um dich besser kennenzulernen. 😊"
        )
        await update.message.reply_text("Wo ist deine Mensa (z. B. Mensa Central)?")
        return CANTEEN

    async def initialize_canteen(self, update: Update, context: CallbackContext):
        """
        Stores the user's canteen and asks for their city.
        """
        key = "canteen"
        next_question = "Wo lebst du? (z. B. Berlin, München, etc.)"
        user_id = update.effective_user.id
        self.user_data_store.setdefault(user_id, {})[key] = update.message.text.strip()
        await update.message.reply_text(next_question)
        return CITY

    async def initialize_city(self, update: Update, context: CallbackContext):
        """
        Stores the user's city and proceeds to ask for transport preference.
        """
        key = "city"
        next_question = "Was ist dein bevorzugtes Transportmittel?"
        user_id = update.effective_user.id
        self.user_data_store.setdefault(user_id, {})[key] = update.message.text.strip()
        await update.message.reply_text(next_question)
        # Returns the next state by calling initialize_transport
        return await self.initialize_transport(update, context)

    async def initialize_transport(self, update: Update, context: CallbackContext):
        """
        Builds a keyboard with transport options if triggered by a message, or
        stores the user's chosen transport if triggered by a callback query.
        """

        def build_transport_keyboard():
            buttons = []
            for mode in TRANSPORT_CATEGORIES:
                buttons.append(
                    [InlineKeyboardButton(mode, callback_data=f"transport:{mode}")]
                )
            return InlineKeyboardMarkup(buttons)

        if update.message:
            keyboard = build_transport_keyboard()
            await update.message.reply_text("Wähle aus diesen Optionen:", reply_markup=keyboard)
            return TRANSPORT
        elif update.callback_query:
            query = update.callback_query
            await query.answer()
            data = query.data.split(":", 1)
            if len(data) == 2 and data[0] == "transport":
                chosen_transport = data[1]
                user_id = update.effective_user.id
                self.user_data_store.setdefault(user_id, {})["transport"] = chosen_transport
                await query.edit_message_text(
                    f"Dein bevorzugtes Transportmittel: {chosen_transport}"
                )
                await query.message.reply_text(
                    "Welche Lieblingsaktien hast du? (Kommagetrennt, z.B. Apple, Tesla)"
                )
                return STOCKS
            return TRANSPORT

    async def initialize_stocks(self, update: Update, context: CallbackContext):
        """
        Stores the user's favorite stocks and asks about relevant news topics.
        """
        user_id = update.effective_user.id
        self.user_data_store.setdefault(user_id, {})["stocks"] = [
            stock.strip() for stock in update.message.text.split(",")
        ]
        await update.message.reply_text("An welchen Nachrichtenthemen bist du interessiert?")
        return await self.initialize_news(update, context)

    async def initialize_news(self, update: Update, context: CallbackContext):
        """
        Presents a list of news categories. Stores the user's selection upon completion.
        """

        def build_news_keyboard(selected):
            inline_buttons = []
            for cat in NEWS_CATEGORIES:
                label = cat + (" ✔" if cat in selected else "")
                inline_buttons.append([InlineKeyboardButton(label, callback_data=f"news:{cat}")])
            inline_buttons.append([InlineKeyboardButton("Fertig", callback_data="news:submit")])
            return InlineKeyboardMarkup(inline_buttons)

        # Triggered by a message
        if update.message:
            context.user_data["selected_news"] = []
            keyboard = build_news_keyboard(context.user_data["selected_news"])
            await update.message.reply_text("Wähle aus diesen Optionen:", reply_markup=keyboard)
            return NEWS
        # Triggered by an inline button
        elif update.callback_query:
            query = update.callback_query
            await query.answer()
            if "selected_news" not in context.user_data:
                context.user_data["selected_news"] = []
            data = query.data.split(":", 1)
            if len(data) == 2 and data[0] == "news":
                if data[1] == "submit":
                    user_id = query.from_user.id
                    self.user_data_store.setdefault(user_id, {})["news"] = context.user_data["selected_news"]
                    joined_news = ", ".join(context.user_data["selected_news"])
                    await query.edit_message_text(f"Deine Nachrichtenthemen: {joined_news}")
                    return await self.end_initialization(update, context)
                category = data[1]
                if category in context.user_data["selected_news"]:
                    context.user_data["selected_news"].remove(category)
                else:
                    context.user_data["selected_news"].append(category)
                new_keyboard = build_news_keyboard(context.user_data["selected_news"])
                await query.edit_message_reply_markup(reply_markup=new_keyboard)
            return NEWS

    async def end_initialization(self, update: Update, context: CallbackContext):
        """
        Provides a summary of the user's preferences, sends them to the API, 
        and ends the conversation.
        """
        user_id = update.effective_user.id
        user_info = self.user_data_store.get(user_id, {})
        summary = (
            "Danke für deine Antworten! Hier ist deine Übersicht:\n\n"
            f"📚 Kurs: {user_info.get('course', 'Nicht angegeben')}\n"
            f"🍽️ Mensa: {user_info.get('canteen', 'Nicht angegeben')}\n"
            f"🏠 Wohnort: {user_info.get('city', 'Nicht angegeben')}\n"
            f"🚆 Transport: {user_info.get('transport', 'Nicht angegeben')}\n"
            f"📈 Aktien: {', '.join(user_info.get('stocks', []))}\n"
            f"📰 Nachrichten: {', '.join(user_info.get('news', []))}"
        )
        if update.message:
            await update.message.reply_text(summary)
            await update.message.reply_text(api_client.post_preferences(user_id, user_info))
            await update.message.reply_text(
                "Klicke jederzeit auf das Menü, um die Präferenzen zu ändern."
            )
        elif update.callback_query:
            await update.callback_query.message.reply_text(summary)
            await update.callback_query.message.reply_text(
                api_client.post_preferences(user_id, user_info)
            )
            await update.callback_query.message.reply_text(
                "Klicke jederzeit auf das Menü, um die Präferenzen zu ändern."
            )

        return ConversationHandler.END

