import random
import re
from typing import List, Tuple

from src.data_process.utils.utils import get_list_sncf_city_from_file, simple_cleaning
from data.data_need import villes_france


def replace_and_generate_response(dataset: List[str]) -> List[Tuple[str, dict]]:
    """
    Remplace 'X', 'Y', et 'C' dans des phrases avec des noms de villes aléatoires.
    Génère une liste d'exemples annotés pour SpaCy.

    :param dataset: Liste des phrases à traiter.
    :return: Liste de tuples au format (phrase, {"entities": [...]}) pour SpaCy.
    """
    processed_data = []
    words_to_use = get_list_sncf_city_from_file()

    for phrase in dataset:
        phrase = simple_cleaning(phrase)
        for _ in range(10):
            modified_phrase = phrase
            reponse = {"entities": []}

            offset = 0

            for match in re.finditer(r"\b[XYC]\b", modified_phrase):
                stripped_word = match.group()

                if words_to_use == []:
                    random_city = random.choice(villes_france).lower()
                    villes_france.remove(random_city)
                else :
                    random_city = random.choice(words_to_use)
                    words_to_use.remove(random_city)

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

