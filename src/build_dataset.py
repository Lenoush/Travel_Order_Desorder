import csv
import requests
import pandas as pd
import random
import re

def get_random_word_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        words = [row['LIBELLE'] for row in reader]
    return random.choice(words)

# def write_data_to_csv(data, filename="/Users/lenaoudjman/Desktop/Travel_order_resolver/data/dataset_sentences.csv"):
#     with open(filename, mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file)
#         writer.writerow(["Phrase", "Reponse"])
#         for phrase in data:
#             reponse = [None, None, None]
#             for words in phrase.split():
#                 if any(word.strip('.,;!?') in ["X", "Y", "C"] for word in words):
#                     random_word = get_random_word_from_file("/Users/lenaoudjman/Desktop/Travel_order_resolver/data/liste_des_gares.csv")
#                     phrase = phrase.replace(words, random_word)
#                     if word == X : append[0], if Y append [-1], else append[1]
#                     reponse.append(random_word)
#             writer.writerow([phrase, " ".join(reponse)])

def write_data_to_csv(data, filename="/Users/lenaoudjman/Desktop/Travel_order_resolver/data/dataset_sentences.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Phrase", "Reponse"])
        for phrase in data:
            reponse = [None, None, None]
            for word in phrase.split():
                stripped_word = word.strip('.,;!?')
                if stripped_word in ["X", "Y", "C"]:
                    random_word = get_random_word_from_file("/Users/lenaoudjman/Desktop/Travel_order_resolver/data/liste_des_gares.csv")
                    phrase = phrase.replace(word, random_word)
                    if stripped_word == "X":
                        reponse[0] = random_word
                    elif stripped_word == "Y":
                        reponse.insert(1, random_word)
                    elif stripped_word == "C":
                        reponse[-1] = random_word
            writer.writerow([phrase, " ".join(filter(None, reponse))])

import data.example_sentences as es
write_data_to_csv(es.data)


def load_sncf_data(name_save= "/Users/lenaoudjman/Desktop/Travel_order_resolver/data/liste_des_gares.csv"):
    # URL du jeu de données SNCF
    url = "https://ressources.data.sncf.com/explore/dataset/liste-des-gares/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true"

    # Requête pour récupérer les données au format CSV
    response = requests.get(url)
    with open(name_save, 'wb') as file:
        file.write(response.content)
    df = pd.read_csv(name_save)
    return df

