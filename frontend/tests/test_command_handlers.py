import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call # import call

# Annahme: pref_config existiert und enthält die Konstanten
# Es wäre gut, die Konstanten zu importieren, um sie in states zu prüfen
# from pref_config import CANTEEN, CITY, ...

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from command_handlers import CommandHandlers # noqa: E402


class TestCommandHandlers(unittest.TestCase):
    @patch("command_handlers.CommandHandler")
    @patch("command_handlers.ConversationHandler")
    @patch("command_handlers.PreferenceHandler")
    @patch("command_handlers.StartHandler")
    def test_configure_conversation_handlers(
        self,
        mock_start_handler_cls,
        mock_preference_handler_cls,
        mock_conversation_handler,
        mock_command_handler,
    ):
        # StartHandler und PreferenceHandler simulieren
        mock_start_handler = MagicMock()
        mock_start_handler_cls.return_value = mock_start_handler

        mock_pref_handler = MagicMock()
        mock_preference_handler_cls.return_value = mock_pref_handler

        # Mocks für die Instanzen, die von den Handlern zurückgegeben werden (wichtig für add_handler Check)
        mock_init_conv_instance = MagicMock(name="InitConvHandlerInstance")
        mock_update_conv_instance = MagicMock(name="UpdateConvHandlerInstance")
        mock_showpref_cmd_instance = MagicMock(name="ShowPrefCmdHandlerInstance")

        # Konfigurieren, was die Handler-Klassen zurückgeben
        mock_conversation_handler.side_effect = [mock_init_conv_instance, mock_update_conv_instance]
        # Annahme: Der 3. Aufruf von CommandHandler ist der für "showpref"
        # Die ersten beiden sind die entry_points der ConversationHandler
        mock_command_handler.side_effect = [MagicMock(), MagicMock(), mock_showpref_cmd_instance]


        # Anwendungs-Objekt simulieren
        application_mock = MagicMock()
        application_mock.add_handler = MagicMock() # Sicherstellen, dass add_handler gemockt ist

        # Zu testende Klasse anlegen
        cmd_handlers = CommandHandlers()

        # Aufruf
        cmd_handlers.configure_conversation_handlers(application_mock)

        # Prüfen, ob ConversationHandler zwei Mal instanziert wurde:
        self.assertEqual(mock_conversation_handler.call_count, 2)

        # Beide Aufrufe des ConversationHandlers extrahieren
        call_list = mock_conversation_handler.call_args_list

        # --- Korrigierte Extraktion der Argumente ---
        # Erster Aufruf (init_handler)
        init_handler_call = call_list[0]
        init_handler_pos_args = init_handler_call.args # oder init_handler_call[0] -> sollte leer sein
        init_handler_kwargs = init_handler_call.kwargs # oder init_handler_call[1] -> enthält die Argumente

        # Zweiter Aufruf (update_handler)
        update_handler_call = call_list[1]
        update_handler_pos_args = update_handler_call.args # oder update_handler_call[0] -> sollte leer sein
        update_handler_kwargs = update_handler_call.kwargs # oder update_handler_call[1] -> enthält die Argumente
        # --- Ende Korrektur ---

        # 1. ConversationHandler (init_handler) prüfen - jetzt mit kwargs
        self.assertEqual(init_handler_pos_args, ()) # Sicherstellen, dass keine pos args da sind
        self.assertIn("entry_points", init_handler_kwargs)
        self.assertIsInstance(init_handler_kwargs["entry_points"], list) # Sollte eine Liste sein
        self.assertIn("states", init_handler_kwargs)
        self.assertIsInstance(init_handler_kwargs["states"], dict) # Sollte ein Dict sein
        self.assertIn("fallbacks", init_handler_kwargs)
        # Hier könntest du detailliertere Prüfungen für states hinzufügen,
        # z.B. ob die richtigen Konstanten als Keys verwendet werden und
        # ob die Werte Listen mit MessageHandler/CallbackQueryHandler-Mocks sind.
        # Dafür müsstest du die Rückgabewerte von mock_message_handler etc. genauer prüfen.

        # 2. ConversationHandler (update_handler) prüfen - jetzt mit kwargs
        self.assertEqual(update_handler_pos_args, ()) # Sicherstellen, dass keine pos args da sind
        self.assertIn("entry_points", update_handler_kwargs)
        self.assertIsInstance(update_handler_kwargs["entry_points"], list)
        self.assertIn("states", update_handler_kwargs)
        self.assertIsInstance(update_handler_kwargs["states"], dict)
        self.assertIn("fallbacks", update_handler_kwargs)
        # Auch hier detailliertere Prüfungen möglich.

        # Prüfen, ob application.add_handler() aufgerufen wurde
        self.assertEqual(application_mock.add_handler.call_count, 3)

        # Prüfen, ob die *korrekten* Handler-Instanzen hinzugefügt wurden
        application_mock.add_handler.assert_has_calls(
            [
                call(mock_init_conv_instance),   # Die Instanz vom 1. ConversationHandler-Aufruf
                call(mock_update_conv_instance), # Die Instanz vom 2. ConversationHandler-Aufruf
                call(mock_showpref_cmd_instance) # Die Instanz vom 3. CommandHandler-Aufruf (für showpref)
            ],
            any_order=True # Reihenfolge der add_handler-Aufrufe ist nicht garantiert
        )

        # Prüfen, ob CommandHandler("showpref", ...) korrekt *instanziiert* wurde
        # (Diese Prüfung ist etwas redundant, wenn der add_handler-Check oben erfolgreich ist,
        #  aber schadet nicht zur Verifizierung der Argumente)
        mock_command_handler.assert_any_call("showpref", mock_pref_handler.show_preferences)


if __name__ == "__main__":
    unittest.main()