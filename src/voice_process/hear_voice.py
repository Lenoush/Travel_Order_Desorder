import speech_recognition as sr
import threading
import keyboard


def stop_listening(recognizer, source):
    print("Fin de l'enregistrement.")
    recognizer.stop_listening()


def on_key_press(key_pressed):
    key_pressed[0] = True


# Fonction pour écouter et transcrire
def listen_for_audio(duration=10):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Parlez maintenant... (Appuyez sur une touche pour arrêter)")

        # Ajuster pour le bruit ambiant
        recognizer.adjust_for_ambient_noise(source)

        stop_event = threading.Event()

        if duration:
            threading.Timer(duration, stop_event.set).start()

        def check_for_keyboard():
            while not stop_event.is_set():
                if keyboard.is_pressed("space"):
                    stop_event.set()

        threading.Thread(target=check_for_keyboard).start()
        audio = recognizer.listen(source, phrase_time_limit=duration)

    try:
        texte = recognizer.recognize_google(audio, language="fr-FR")
        print("Texte transcrit : ", texte)
    except sr.UnknownValueError:
        print("L'audio n'a pas été compris")
    except sr.RequestError as e:
        print(f"Erreur lors de la requête : {e}")


listen_for_audio()
