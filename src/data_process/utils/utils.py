import csv
import os
import random
import re
from typing import List

import pandas as pd
import requests
from unidecode import unidecode

from data.data_need import ville_sans_gare, villes_france
from config import SNCF_gare


def clean_word(word: str) -> str:
    """
    Cleans a word by removing any parentheses and leading/trailing whitespace.
    """
    # Remove any parentheses and leading/trailing whitespace
    cleaned_word = re.sub(r"\s*\(.*?\)", "", word).strip()

    # Remove any TGV word and the '-' character
    cleaned_word = re.sub(r"(-?TGV-?)", "", cleaned_word).strip()

    # Remove any digits
    cleaned_word = re.sub(r"\d+", "", cleaned_word).strip()

    # Add a hyphen between 'La' or 'Le' and the final word if they are separated by a space
    cleaned_word = re.sub(r"\b(-la|-le|-les)\s+(\w+)", r"\1-\2", cleaned_word)
    cleaned_word = re.sub(r"\b(-La|-Le|-Les)\s+(\w+)", r"\1-\2", cleaned_word)

    # Remove any trailing 'TT' characters
    cleaned_word = re.sub(r"TT$", "", cleaned_word).strip()

    # Remove "tram-train"
    cleaned_word = re.sub(r"tram-train", "", cleaned_word)

    return cleaned_word


def write_data_to_csv(data: List[List[str]], filename: str) -> None:
    """
    Writes the processed phrases and corresponding responses to a CSV file.
    """

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Phrase", "Reponse"])
        writer.writerows(data)


def merge_datasets(*datasets: List[str]) -> List[str]:
    """
    Merges multiple datasets into one.
    """

    merged_data = []
    for dataset in datasets:
        merged_data.extend(dataset)
    random.shuffle(merged_data)
    return merged_data


def get_list_sncf_city_from_file() -> str:
    with open(SNCF_gare, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        words = []
        for row in reader:
            cleaned_word = clean_word(row["LIBELLE"])
            words.append(cleaned_word.lower())
    words.extend(ville_sans_gare)
    return words

def get_random_ville_france() -> str:
    return random.choice(villes_france)


def load_sncf_data() -> pd.DataFrame:
    """
    Downloads SNCF station data from the specified URL, saves it locally,
    and returns the data as a Pandas DataFrame.
    """

    url = (
        "https://ressources.data.sncf.com/explore/dataset/liste-des-gares/download/?format=csv&timezone=Europe"
        "/Berlin&use_labels_for_header=true"
    )

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


def load_data(dataset_path) -> tuple[List, List]:
    """
    Loads the dataset from the specified path and extracts the 'Phrase' and 'Reponse' columns.
    """
    df: pd.DataFrame = pd.read_csv(dataset_path)
    phrases = df["Phrase"].tolist()
    responses = df["Reponse"].tolist()
    return phrases, responses

def simple_cleaning(phrase: str) -> str:
    """
    Cleans a phrase by removing any parentheses and leading/trailing whitespace.
    """
    # Remove any ponctuation
    # cleaned_phrase = re.sub(r"[^\w\s]", "", phrase)
    cleaned_phrase = phrase
    # Remove any accents
    cleaned_phrase = unidecode(cleaned_phrase)

    # Add point a la fin de chaque phrase
    cleaned_phrase = cleaned_phrase + "."

    return cleaned_phrase