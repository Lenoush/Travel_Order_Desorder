import re
from typing import List

from src.data_process.utils.utils import get_random_word_from_file


def replace_and_generate_response(dataset: List[str]) -> List[List[str]]:
    """
    Replace 'X', 'Y', and 'C' in phrases with random city names and generate responses.
    Each phrase is recorded 5 times with different city names.
    """
    processed_data = []

    for phrase in dataset:
        for _ in range(50):
            reponse = [None, None, None]
            modified_phrase = phrase
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
                    reponse[0] = random_city
                elif stripped_word == "C":
                    reponse.insert(1, random_city)
                elif stripped_word == "Y":
                    reponse[-1] = random_city

            processed_data.append([modified_phrase, ":".join(filter(None, reponse))])
    return processed_data


def replace_and_generate_error(dataset: List[str]) -> List[List[str]]:
    """
    Replace 'X' in phrases with a random city name and generate an error response.
    Each phrase is recorded 5 times with different city names.
    """
    processed_data = []
    for phrase in dataset:
        for _ in range(20):
            reponse = ["Error"]
            modified_phrase = phrase
            for word in modified_phrase.split():
                stripped_word = word.strip(".,;!?")
                if stripped_word == "X":
                    random_word = get_random_word_from_file().lower()
                    modified_phrase = modified_phrase.replace(word, random_word, 1)
            processed_data.append([modified_phrase, ":".join(reponse)])
    return processed_data
