import requests
import pandas as pd
import csv
import random

from config import SNCF_gare, Dataset

def get_random_word_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        words = [row['LIBELLE'] for row in reader]
    return random.choice(words)

def write_data_to_csv(data, filename=Dataset):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Phrase", "Reponse"])
        for phrase in data:
            reponse = [None, None, None]
            for word in phrase.split():
                stripped_word = word.strip('.,;!?')
                if stripped_word in ["X", "Y", "C"]:
                    random_word = get_random_word_from_file(SNCF_gare)
                    phrase = phrase.replace(word, random_word)
                    if stripped_word == "X":
                        reponse[0] = random_word
                    elif stripped_word == "Y":
                        reponse.insert(1, random_word)
                    elif stripped_word == "C":
                        reponse[-1] = random_word
            writer.writerow([phrase, ":".join(filter(None, reponse))])

def load_sncf_data():
    url = "https://ressources.data.sncf.com/explore/dataset/liste-des-gares/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true"

    response = requests.get(url)
    with open(SNCF_gare, 'wb') as file:
        file.write(response.content)
    df = pd.read_csv(SNCF_gare)
    return df

