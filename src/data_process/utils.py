import csv
import os
import random
from typing import List, Any

import pandas as pd
import requests
import re

from config import SNCF_gare
from data.data_need import ville_sans_gare


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
    # cleaned_word = re.sub(r"\b(La|Le)\s+(\w+)", r"\1-\2", cleaned_word)

    # Remove any trailing 'TT' characters
    cleaned_word = re.sub(r"TT$", "", cleaned_word).strip()

    return cleaned_word


def get_random_word_from_file() -> str:
    """
    Reads a CSV file and returns a random word from the 'LIBELLE' column.
    """

    with open(SNCF_gare, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        words = []
        for row in reader:
            cleaned_word = clean_word(row["LIBELLE"])
            words.append(cleaned_word)
    words.extend(ville_sans_gare)
    return random.choice(words)


get_random_word_from_file()


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


def replace_and_generate_response(dataset: List[str]) -> List[List[str]]:
    """
    Replace 'X', 'Y', and 'C' in phrases with random city names and generate responses.
    Each phrase is recorded 5 times with different city names.
    """
    processed_data = []
    for phrase in dataset:
        for _ in range(20):
            reponse = [None, None, None]
            modified_phrase = phrase
            words_add = []
            for word in modified_phrase.split():
                stripped_word = word.strip(".,;!?")
                if stripped_word in ["X", "Y", "C"]:
                    random_word = get_random_word_from_file().lower()
                    while random_word in words_add:
                        random_word = get_random_word_from_file().lower()
                    modified_phrase = modified_phrase.replace(word, random_word, 1)
                    if stripped_word == "X":
                        reponse[0] = random_word
                    elif stripped_word == "C":
                        reponse.insert(1, random_word)
                    elif stripped_word == "Y":
                        reponse[-1] = random_word
                    words_add.append(random_word)
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
