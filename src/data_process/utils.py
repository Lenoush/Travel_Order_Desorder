import csv
import os
import random
from typing import List, Any

import pandas as pd
import requests

from config import SNCF_gare
from data.data_need import ville_sans_gare


def get_random_word_from_file() -> str:
    """
    Reads a CSV file and returns a random word from the 'LIBELLE' column.
    """

    with open(SNCF_gare, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        words = [row["LIBELLE"] for row in reader]
    words.extend(ville_sans_gare)
    return random.choice(words)


def load_sncf_data() -> pd.DataFrame:
    """
    Downloads SNCF station data from the specified URL, saves it locally,
    and returns the data as a Pandas DataFrame.
    """

    url = ("https://ressources.data.sncf.com/explore/dataset/liste-des-gares/download/?format=csv&timezone=Europe"
           "/Berlin&use_labels_for_header=true")

    response = requests.get(url)

    # check master directory of file exist
    if not os.path.exists(os.path.dirname(SNCF_gare)):
        os.makedirs(os.path.dirname(SNCF_gare))
    # if file does not exist create it
    if not os.path.exists(SNCF_gare):
        with open(SNCF_gare, "w"):
            pass

    with open(SNCF_gare, "wb") as file:
        file.write(response.content)
    df = pd.read_csv(SNCF_gare)
    return df


def replace_and_generate_response(dataset: List[str]) -> List[List[str]]:
    """
    Replace 'X', 'Y', and 'C' in phrases with random city names and generate responses.
    Each phrase is recorded 5 times with different city names.
    """
    processed_data = []
    for phrase in dataset:
        for _ in range(5):
            reponse = [None, None, None]
            modified_phrase = phrase
            for word in modified_phrase.split():
                stripped_word = word.strip(".,;!?")
                if stripped_word in ["X", "Y", "C"]:
                    random_word = get_random_word_from_file().lower()
                    modified_phrase = modified_phrase.replace(word, random_word, 1)
                    if stripped_word == "X":
                        reponse[0] = random_word
                    elif stripped_word == "C":
                        reponse.insert(1, random_word)
                    elif stripped_word == "Y":
                        reponse[-1] = random_word
            processed_data.append([modified_phrase, ":".join(filter(None, reponse))])
    return processed_data


def replace_and_generate_error(dataset: List[str]) -> List[List[str]]:
    """
    Replace 'X' in phrases with a random city name and generate an error response.
    Each phrase is recorded 5 times with different city names.
    """
    processed_data = []
    for phrase in dataset:
        for _ in range(2):
            reponse = ["Error"]
            modified_phrase = phrase
            for word in modified_phrase.split():
                stripped_word = word.strip(".,;!?")
                if stripped_word == "X":
                    random_word = get_random_word_from_file().lower()
                    modified_phrase = modified_phrase.replace(word, random_word, 1)
            processed_data.append([modified_phrase, ":".join(reponse)])
    return processed_data


def merge_datasets(*datasets: List[str]) -> List[str]:
    """
    Merges multiple datasets into one.
    """

    merged_data = []
    for dataset in datasets:
        merged_data.extend(dataset)
    random.shuffle(merged_data)
    return merged_data


def write_data_to_csv(data: List[List[str]], filename: str) -> None:
    """
    Writes the processed phrases and corresponding responses to a CSV file.
    """

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Phrase", "Reponse"])
        writer.writerows(data)


def load_data(dataset_path) -> tuple[Any, Any]:
    """
    Loads the dataset from the specified path and extracts the 'Phrase' and 'Reponse' columns.
    """
    df: pd.DataFrame = pd.read_csv(dataset_path)
    phrases = df["Phrase"].tolist()
    responses = df["Reponse"].tolist()
    return phrases, responses
