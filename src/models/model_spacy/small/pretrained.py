import re
import sys
import spacy
import pandas as pd
from config import Valid, Output_model
from src.data_process.utils import load_data


class Evaluators:

    def __init__(self, data: pd.DataFrame, model_size: spacy):
        """
        Initializes the EntityEvaluator.
        """
        model_map = {
            "none_small": spacy.load("fr_core_news_sm"),
            "none_medium": spacy.load("fr_core_news_md"),
            "none_large": spacy.load("fr_core_news_lg"),
            "small": spacy.load(Output_model + "model_spacy/small/small_trained.model"),
            "medium": spacy.load(
                Output_model + "model_spacy/small/medium_trained.model"
            ),
            "large": spacy.load(Output_model + "model_spacy/small/large_trained.model"),
        }
        if model_size not in model_map:
            raise ValueError("Model size must be something specific.")

        self.model = model_map[model_size]
        self.phrases, self.responses = load_data(data)
        self.model_small = spacy.load("fr_core_news_sm")
        self.symbols = ["-", "'", "`", "‘", "’", "´", "ˋ"]

    def lemmatize_phrase(self, phrase: str) -> str:
        """
        Lemmatizes the input phrase.
        """
        doc = self.model(phrase)
        lemmatized = []

        for token in doc:
            if token.pos_ == "VERB":
                lemmatized.append(f" {token.lemma_} ")
            elif token.text in self.symbols:
                lemmatized.append(token.text)
            elif len(lemmatized) > 0 and lemmatized[-1] in self.symbols:
                lemmatized.append(token.text)
            else:
                lemmatized.append(f" {token.text}")

        return "".join(lemmatized).strip()

    def is_question(self, phrase: str) -> bool:
        """
        Determines if the given phrase is a question.
        """
        mots_interrogatifs = [
            "qui",
            "quoi",
            "où",
            "quand",
            "comment",
            "pourquoi",
            "lequel",
            "faut-il",
        ]
        return (
            any(token.lemma_ in mots_interrogatifs for token in self.model(phrase))
            or "?" in phrase
        )

    def extract_cities(self, phrase):
        doc = self.model(phrase)
        return [ent.text for ent in doc.ents if ent.label_ == "LOC"], doc

    def evaluate_without_rules(self) -> None:
        """
        Evaluates entity recognition without using any custom rules.
        """
        correct = 0
        total = len(self.phrases)

        for phrase, reponse in zip(self.phrases, self.responses):
            predicted_cities, _ = self.extract_cities(phrase)

            if reponse == "Error":
                expected_cities = []
            else:
                expected_cities = reponse.split(":")

            if predicted_cities == expected_cities:
                correct += 1
            else:
                # print(predicted_cities, expected_cities)
                # print(phrase)
                pass

        print("Without rules")
        accuracy = (correct / total) * 100
        print(f"Accuracy: {accuracy:.2f}%")

    def remove_duplicates(self, cities):
        """
        Removes duplicate cities from the list of predicted cities.
        """
        return list(dict.fromkeys(cities))

    def evaluate_with_rules(self) -> None:
        """
        Evaluates entity recognition with custom rules.
        """
        correct = 0
        total = len(self.phrases)
        mauvaise_correspondance = 0

        for phrase, reponse in zip(self.phrases, self.responses):
            predicted_cities, doc = self.extract_cities(phrase)

            predicted_cities = self.remove_duplicates(predicted_cities)

            # Remove si l'entité est un RER
            for i, ville in enumerate(predicted_cities):
                if "RER" in ville:
                    predicted_cities.remove(ville)
                    continue
                # Remove si le mot d'avant la ville est un verbe d'appel
                lemmatized_phrase = self.lemmatize_phrase(phrase)
                index = lemmatized_phrase.find(ville)
                if index > 0:
                    words_before_city = lemmatized_phrase[:index].split()
                    if words_before_city:
                        last_word_before_city = words_before_city[-1]
                        if last_word_before_city in [
                            "appeler",
                            "nommer",
                            "surnommer",
                            "avec",
                        ]:
                            predicted_cities.remove(ville)
                # Corriger les villes  (-, ')
                hyphenated_matches = re.findall(r"\b[\w']+(?:-[\w']+)+\b", phrase)
                for hyphenated in hyphenated_matches:
                    if ville in hyphenated:
                        predicted_cities[i] = hyphenated

                # Respacy le mot
                # doc2 = self.model_small(ville)
                # print([ent.label_ for ent in doc2.ents], ville)

            # Appliquer les règles
            if len(predicted_cities) < 2:
                predicted_cities = []

            if reponse == "Error":
                expected_cities = []
            else:
                expected_cities = reponse.split(":")

            if predicted_cities == expected_cities:
                correct += 1
            else:
                if sorted(predicted_cities) == sorted(expected_cities):
                    mauvaise_correspondance += 1
                else:
                    # print(predicted_cities, expected_cities)
                    # print([ent.label_ for ent in doc.ents])
                    # print(phrase)
                    pass

        accuracy = (correct / total) * 100
        print("With rules")
        print(f"Accuracy: {accuracy:.2f}%")


def main():
    if len(sys.argv) != 2:
        print("Usage: python trainning.py <model_size>")
        print(
            "model_size: 'none_small', 'none_medium', 'none_large' , 'small' , 'medium' or 'large'"
        )
        sys.exit(1)

    model_size = sys.argv[1]

    print(f"Spacy model {model_size}")
    evaluator = Evaluators(Valid, model_size)
    evaluator.evaluate_without_rules()
    print("\n")
    evaluator.evaluate_with_rules()
    print("\n")


if __name__ == "__main__":
    main()
