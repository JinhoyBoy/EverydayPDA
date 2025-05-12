import os
import sys

import unittest
from unittest.mock import patch, MagicMock, mock_open
import speech_recognition as sr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from speech_utils import generate_voice_message, convert_voice_to_text


class TestSpeechUtils(unittest.TestCase):
    @patch("speech_utils.gTTS")
    @patch("speech_utils.tempfile.NamedTemporaryFile")
    @patch("speech_utils.subprocess.run")
    @patch("speech_utils.os.unlink")
    def test_generate_voice_message_success(
        self, mock_unlink, mock_subprocess_run, mock_tempfile, mock_gtts
    ):
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/fakefile.mp3"
        mock_tempfile.return_value = mock_temp

        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance

        result = generate_voice_message("Hallo Welt")
        self.assertIn("output.ogg", result)
        mock_gtts.assert_called_once_with(text="Hallo Welt", lang="de")
        mock_tts_instance.save.assert_called_once_with("/tmp/fakefile.mp3")
        mock_subprocess_run.assert_called_once()
        mock_unlink.assert_called_once_with("/tmp/fakefile.mp3")

    def test_generate_voice_message_empty_text(self):
        with self.assertRaises(ValueError):
            generate_voice_message("   ")

    @patch("speech_utils.os.path.exists", return_value=False)
    def test_convert_voice_to_text_file_not_found(self, mock_exists):
        with self.assertRaises(FileNotFoundError):
            convert_voice_to_text("/path/does/not/exist.ogg")

    @patch("speech_utils.os.path.exists", return_value=True)
    @patch("speech_utils.tempfile.NamedTemporaryFile")
    @patch("speech_utils.subprocess.run")
    @patch("speech_utils.os.unlink")
    @patch("speech_utils.open", new_callable=mock_open, read_data=b"FAKE AUDIO DATA")
    @patch("speech_utils.gSTT.Recognizer")
    def test_convert_voice_to_text_success(
        self,
        mock_recognizer_cls,
        mock_file_open,
        mock_unlink,
        mock_subprocess_run,
        mock_tempfile,
        mock_exists
    ):
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.return_value = "Hallo erkannt"
        mock_recognizer_cls.return_value = mock_recognizer

        mock_temp = MagicMock()
        mock_temp.name = "/tmp/fakefile.wav"
        mock_tempfile.return_value = mock_temp

        result = convert_voice_to_text("/path/to/input.ogg")
        self.assertEqual(result, "Hallo erkannt")
        mock_subprocess_run.assert_called_once()
        mock_file_open.assert_called_with("/tmp/fakefile.wav", "rb")
        mock_unlink.assert_called_once_with("/tmp/fakefile.wav")

    @patch("speech_utils.os.path.exists", return_value=True)
    @patch("speech_utils.tempfile.NamedTemporaryFile")
    @patch("speech_utils.subprocess.run")
    @patch("speech_utils.os.unlink")
    @patch("speech_utils.open", new_callable=mock_open, read_data=b"FAKE AUDIO DATA")
    @patch("speech_utils.gSTT.Recognizer")
    def test_convert_voice_to_text_unknown_value(
        self,
        mock_recognizer_cls,
        mock_file_open,
        mock_unlink,
        mock_subprocess_run,
        mock_tempfile,
        mock_exists
    ):
        mock_recognizer = MagicMock()
        # Jetzt wirklich eine UnknownValueError aus speech_recognition auslösen.
        mock_recognizer.recognize_google.side_effect = sr.UnknownValueError()
        mock_recognizer_cls.return_value = mock_recognizer

        mock_temp = MagicMock()
        mock_temp.name = "/tmp/fakefile.wav"
        mock_tempfile.return_value = mock_temp

        result = convert_voice_to_text("/path/to/input.ogg")
        self.assertIn("Ich konnte die Sprache nicht verstehen.", result)
        mock_subprocess_run.assert_called_once()
        mock_file_open.assert_called_with("/tmp/fakefile.wav", "rb")
        mock_unlink.assert_called_once_with("/tmp/fakefile.wav")

    @patch("speech_utils.os.path.exists", return_value=True)
    @patch("speech_utils.tempfile.NamedTemporaryFile")
    @patch("speech_utils.subprocess.run")
    @patch("speech_utils.os.unlink")
    @patch("speech_utils.open", new_callable=mock_open, read_data=b"FAKE AUDIO DATA")
    @patch("speech_utils.gSTT.Recognizer")
    def test_convert_voice_to_text_request_error(
        self,
        mock_recognizer_cls,
        mock_file_open,
        mock_unlink,
        mock_subprocess_run,
        mock_tempfile,
        mock_exists
    ):
        mock_recognizer = MagicMock()
        # Jetzt eine RequestError auslösen
        mock_recognizer.recognize_google.side_effect = sr.RequestError("API nicht erreichbar")
        mock_recognizer_cls.return_value = mock_recognizer

        mock_temp = MagicMock()
        mock_temp.name = "/tmp/fakefile.wav"
        mock_tempfile.return_value = mock_temp

        result = convert_voice_to_text("/path/to/input.ogg")
        self.assertIn("Fehler: Ich kann die Spracherkennung gerade nicht erreichen.", result)
        mock_subprocess_run.assert_called_once()
        mock_file_open.assert_called_with("/tmp/fakefile.wav", "rb")
        mock_unlink.assert_called_once_with("/tmp/fakefile.wav")


if __name__ == "__main__":
    unittest.main()