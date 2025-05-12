import os
import tempfile
import subprocess
import speech_recognition as gSTT
from gtts import gTTS

# Base directory for audio files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_voice_message(text: str) -> str:
    """
    Converts the given text into an OGG file and returns its path.
    The user-facing error messages remain in German as requested.

    :param text: The text to be converted to speech.
    :return: The file path to the generated OGG file.
    :raises ValueError: If the provided text is empty or whitespace.
    """
    if not text.strip():
        raise ValueError("Text darf nicht leer sein.")

    # Create a temporary MP3 file
    temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_mp3.close()

    # Convert text to speech (German language)
    tts = gTTS(text=text, lang="de")
    tts.save(temp_mp3.name)

    # Use ffmpeg to create the OGG file
    ogg_path = os.path.join(BASE_DIR, "output.ogg")
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", temp_mp3.name,
            "-acodec", "libvorbis", "-ar", "24000", "-ab", "64k", ogg_path
        ]
    )

    # Remove the temporary MP3 file
    os.unlink(temp_mp3.name)

    return ogg_path


def convert_voice_to_text(file_path: str) -> str:
    """
    Converts a given OGG file to text and returns the result.
    User-facing messages remain in German as requested.

    :param file_path: The path to the OGG file.
    :return: The recognized text or an error message in German.
    :raises FileNotFoundError: If the OGG file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Die Datei {file_path} existiert nicht.")

    # Convert OGG to WAV using ffmpeg
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_wav.close()

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", file_path,
            "-ac", "1", "-ar", "16000", "-vn", temp_wav.name
        ]
    )

    # Process the WAV file with speech_recognition
    recognizer = gSTT.Recognizer()
    with open(temp_wav.name, "rb") as wav_file:
        audio_data = gSTT.AudioData(wav_file.read(), 16000, 2)

    # Remove the temporary WAV file
    os.unlink(temp_wav.name)

    # Perform speech recognition
    try:
        text = recognizer.recognize_google(audio_data, language="de-DE")
        return text
    except gSTT.UnknownValueError:
        return "Ich konnte die Sprache nicht verstehen."
    except gSTT.RequestError:
        return "Fehler: Ich kann die Spracherkennung gerade nicht erreichen."
