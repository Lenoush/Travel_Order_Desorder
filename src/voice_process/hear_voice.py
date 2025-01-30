import speech_recognition as sr
from pydub import AudioSegment
import os


def convert_m4a_to_wav(m4a_file):
    """Convertit un fichier m4a en wav."""
    audio = AudioSegment.from_file(m4a_file, format="m4a")
    wav_file = m4a_file.replace(".m4a", ".wav")
    audio.export(wav_file, format="wav")
    return wav_file


def transcribe_audio(file_path):
    """Transcrit le texte à partir d'un fichier audio (wav)."""
    recognizer = sr.Recognizer()

    # Charger le fichier wav
    with sr.AudioFile(file_path) as source:
        print("Chargement du fichier audio...")
        audio = recognizer.record(source)

    try:
        # Transcription avec Google Speech Recognition
        text = recognizer.recognize_google(audio, language="fr-FR")
        print("Texte transcrit : ", text)
        return text
    except sr.UnknownValueError:
        print("L'audio n'a pas été compris.")
    except sr.RequestError as e:
        print(f"Erreur lors de la requête : {e}")
    return None


def process_m4a_file(m4a_file):
    """Processus complet pour convertir un fichier m4a en texte."""
    if not m4a_file.endswith(".m4a"):
        print("Erreur : Le fichier doit être un fichier .m4a.")
        return

    # Convertir le fichier m4a en wav
    wav_file = convert_m4a_to_wav(m4a_file)
    print(f"Fichier converti en : {wav_file}")

    # Transcrire le fichier audio wav
    text = transcribe_audio(wav_file)

    # Supprimer le fichier wav temporaire
    os.remove(wav_file)

    return text
