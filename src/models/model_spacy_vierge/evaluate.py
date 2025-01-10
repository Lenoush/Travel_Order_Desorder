import ast
import pandas as pd
import spacy
from typing import List, Tuple

from config import Valid_vierge, Test_vierge

output_dir = "src/models/model_spacy_vierge/2025-01-09_trained.model"
nlp = spacy.load(output_dir)


def load_data(valid_file: str):
    valid_ = []

    df_train: pd.DataFrame = pd.read_csv(valid_file)

    if not {"Phrase", "Reponse"}.issubset(df_train.columns):
        raise ValueError(
            "Le fichier CSV doit contenir les colonnes 'Phrase' et 'Reponse'."
        )

    for _, row in df_train.iterrows():
        phrase = row["Phrase"]
        annotations = ast.literal_eval(row["Reponse"])
        if not isinstance(annotations, dict) or "entities" not in annotations:
            raise ValueError(
                f"Annotation invalide pour la phrase '{phrase}': {annotations}"
            )

        valid_.append((phrase, annotations))

    return valid_


def evaluate_model(nlp, validation_data: List[Tuple[str, dict]]) -> None:
    """
    Evaluate the spaCy model on the validation dataset.

    Args:
        nlp: The loaded spaCy model.
        validation_data: List of tuples where each tuple contains a text
                         and its annotations (entities).
    """
    total_phrases = len(validation_data)
    correct_phrases = 0

    correct_indices = 0
    total_indices = 0

    for text, annotations in validation_data:
        doc = nlp(text)
        predicted_entities = [
            (ent.start_char, ent.end_char, ent.label_) for ent in doc.ents
        ]
        expected_entities = annotations["entities"]

        # false positives, and false negatives for True accurancy
        false_positives = set(predicted_entities) - set(expected_entities)
        false_negatives = set(expected_entities) - set(predicted_entities)

        if not false_positives and not false_negatives:
            correct_phrases += 1
        # else:
        #     print(f"Phrase: {text}")
        #     print(f"Attendu (Expected): {expected_entities}")
        #     print(f"Prédit (Predicted): {predicted_entities}")
        #     print("-" * 50)

        # Calculate accuracy based on correct entity indices, ignoring entity labels
        total_indices += len(annotations["entities"])

        for expected_entity in annotations["entities"]:
            expected_start, expected_end, _ = expected_entity
            for predicted_entity in predicted_entities:
                predicted_start, predicted_end, _ = predicted_entity
                if expected_start == predicted_start and expected_end == predicted_end:
                    correct_indices += 1
                    break

    # # Calculate index accuracy
    # index_accuracy = correct_indices / total_indices if total_indices > 0 else 0
    # print("\n=== Evaluation des indices ===")
    # print(f"Total indices: {total_indices}")
    # print(f"Indices corrects: {correct_indices}")
    # print(f"Index Accuracy for phrase: {index_accuracy:.2%}")

    # # Calculate accuracy
    accuracy = correct_phrases / total_phrases if total_phrases > 0 else 0
    # print(f"\n=== Résumé de l'évaluation ===")
    # print(f"Total phrases: {total_phrases}")
    # print(f"Phrases correctes: {correct_phrases}")
    # print(f"Accuracy: {accuracy:.2%}")
    return accuracy


data_test = load_data(Test_vierge)
data_valid = load_data(Valid_vierge)
acc_test = evaluate_model(nlp, data_test)
acc_valid = evaluate_model(nlp, data_valid)
print(acc_test, acc_valid)
