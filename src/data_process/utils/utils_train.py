import random
import re
from typing import List

from src.data_process.utils.utils import get_list_sncf_city_from_file
from data.data_need import villes_france


def replace_and_generate_response(dataset: List[str]) -> List[List[str]]:
    """
    Replace 'X', 'Y', and 'C' in phrases with random city names and generate responses.
    Each phrase is recorded 5 times with different city names.
    """
    processed_data = []
    words_to_use = get_list_sncf_city_from_file()


    for phrase in dataset:
        for _ in range(10):
            reponse = [None, None, None]
            modified_phrase = phrase

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
                    reponse[0] = random_city
                elif stripped_word == "C":
                    reponse.insert(1, random_city)
                elif stripped_word == "Y":
                    reponse[-1] = random_city

            processed_data.append([modified_phrase, ":".join(filter(None, reponse))])
    return processed_data
