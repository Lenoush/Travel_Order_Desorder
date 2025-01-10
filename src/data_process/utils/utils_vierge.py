import re
from typing import List, Tuple

from src.data_process.utils.utils import get_random_word_from_file


def replace_and_generate_response(dataset: List[str]) -> List[Tuple[str, dict]]:
    """
    Remplace 'X', 'Y', et 'C' dans des phrases avec des noms de villes aléatoires.
    Génère une liste d'exemples annotés pour SpaCy.

    :param dataset: Liste des phrases à traiter.
    :return: Liste de tuples au format (phrase, {"entities": [...]}) pour SpaCy.
    """
    processed_data = []

    for phrase in dataset:
        for _ in range(50):
            modified_phrase = phrase
            reponse = {"entities": []}
            words_used = []

            offset = 0

            for match in re.finditer(r"\b[XYC]\b", modified_phrase):
                stripped_word = match.group()

                random_city = get_random_word_from_file().lower()
                while random_city in words_used:
                    random_city = get_random_word_from_file().lower()
                words_used.append(random_city)

                start_idx = match.start() + offset
                end_idx = match.end() + offset

                modified_phrase = (
                    modified_phrase[:start_idx]
                    + random_city
                    + modified_phrase[end_idx:]
                )
                offset += len(random_city) - len(stripped_word)

                if stripped_word == "X":
                    reponse["entities"].append(
                        (start_idx, start_idx + len(random_city), "DEPART")
                    )
                elif stripped_word == "C":
                    reponse["entities"].append(
                        (start_idx, start_idx + len(random_city), "CORRESPONDANCE")
                    )
                elif stripped_word == "Y":
                    reponse["entities"].append(
                        (start_idx, start_idx + len(random_city), "ARRIVEE")
                    )

            processed_data.append((modified_phrase, reponse))
    return processed_data


def replace_and_generate_error(dataset: List[str]) -> List[List[str]]:
    """
    Replace 'X' in phrases with a random city name and generate an error response.
    Each phrase is recorded 5 times with different city names.
    """
    processed_data = []
    for phrase in dataset:
        for _ in range(20):
            modified_phrase = phrase
            for word in modified_phrase.split():
                stripped_word = word.strip(".,;!?")
                if stripped_word in ["X", "Y", "C"]:
                    random_word = get_random_word_from_file().lower()
                    modified_phrase = modified_phrase.replace(word, random_word, 1)
            processed_data.append(
                (modified_phrase, {"entities": [(0, len(modified_phrase), "ERROR")]})
            )

    return processed_data
