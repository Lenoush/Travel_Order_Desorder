
import random
import csv

def get_random_word_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        words = [row['LIBELLE'] for row in reader]
    return random.choice(words)
