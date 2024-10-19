import spacy
from config import Output_model, Valid
from src.models.model_spacy.small.trainning import SpacyNERTrainer


# Charger le modèle spaCy de base
nlp = spacy.load("fr_core_news_sm")
trained_model = spacy.load(Output_model + "model_spacy/small/test1.model")

# Listes pour stocker les entités prédites et réelles
y_true = []
y_pred = []

good = 0
bad = 0

valid_dataset = SpacyNERTrainer.load_data(Valid)

# Évaluer le modèle sur les données de validation
for phrase, reponse in valid_dataset:
    doc = trained_model(phrase)
    entities_pred = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]

    y_true.append(reponse["entities"])
    y_pred.append(entities_pred)

    if entities_pred != reponse["entities"]:
        bad += 1
    else:
        good += 1


total = good + bad
print(f"Correct : {(good / total) * 100:.2f}%")
print(f"Incorrect : {(bad / total) * 100:.2f}%")
