import speech_recognition as sr
from pydub import AudioSegment
import os


def convert_m4a_to_wav(m4a_file):
    """Convertit un fichier m4a en wav."""
    audio = AudioSegment.from_file(m4a_file, format="m4a")
    wav_file = m4a_file.replace(".m4a", ".wav")
    audio.export(wav_file, format="wav")
    return wav_file

def convert_webm_to_wav(webm_file):
    """Convertit un fichier webm en wav."""
    audio = AudioSegment.from_file(webm_file, format="webm")
    wav_file = webm_file.replace(".webm", ".wav")
    audio.export(wav_file, format="wav")
    return wav_file


def transcribe_audio(file_path):
    """Transcrit le texte à partir d'un fichier audio (wav)."""
    recognizer = sr.Recognizer()

    # Charger le fichier wav
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="fr-FR")
        return text
    except sr.UnknownValueError:
        print("L'audio n'a pas été compris.")
    except sr.RequestError as e:
        print(f"Erreur lors de la requête : {e}")
    return None


def process_m4a_file(file):
    """Processus complet pour convertir un fichier m4a en texte."""

    if file.endswith(".m4a"):
        wav_file = convert_m4a_to_wav(file)
    elif file.endswith(".webm"):
        wav_file = convert_webm_to_wav(file)
    else : 
        return "Format du fichier non supporté"

    # Transcrire le fichier audio wav
    text = transcribe_audio(wav_file)

    # Supprimer le fichier wav temporaire
    os.remove(wav_file)

    return text
