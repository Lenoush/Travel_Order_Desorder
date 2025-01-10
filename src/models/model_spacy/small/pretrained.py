import spacy
import pandas as pd
from config import Valid, Output_model
from src.data_process.utils import load_data


class Evaluators:

    def __init__(self, data: pd.DataFrame, model: spacy):
        """
        Initializes the EntityEvaluator.
        """
        self.phrases, self.responses = load_data(data)
        self.model = model
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

        print("Without rules")
        accuracy = (correct / total) * 100
        print(f"Accuracy: {accuracy:.2f}%")

    def evaluate_with_rules(self) -> None:
        """
        Evaluates entity recognition with custom rules.
        """
        correct = 0
        total = len(self.phrases)

        for phrase, reponse in zip(self.phrases, self.responses):
            lemmatized_phrase = self.lemmatize_phrase(phrase)
            predicted_cities, doc = self.extract_cities(lemmatized_phrase)

            # Remove si l'entité est un RER
            for ville in predicted_cities:
                if "RER" in ville:
                    predicted_cities.remove(ville)
                    continue
                # Remove si le mot d'avant la ville est un verbe d'appel
                index = lemmatized_phrase.find(ville)
                if index > 0:
                    words_before_city = lemmatized_phrase[:index].split()
                    if words_before_city:
                        last_word_before_city = words_before_city[-1]
                        if last_word_before_city in ["appeler", "nommer", "surnommer"]:
                            predicted_cities.remove(ville)

            # Appliquer les règles
            if not predicted_cities:
                predicted_cities = predicted_cities
            elif len(predicted_cities) < 2:
                predicted_cities = predicted_cities

            if reponse == "Error":
                pass
            else:
                expected_cities = reponse.split(":")

            if predicted_cities == expected_cities:
                correct += 1
            else:
                # print(predicted_cities, expected_cities)
                # print(phrase)
                pass

        accuracy = (correct / total) * 100
        print("With rules")
        print(f"Accuracy: {accuracy:.2f}%")


def main():

    # Initialize evaluator
    # evaluator = Evaluators(Valid, spacy.load("fr_core_news_sm"))
    evaluator = Evaluators(
        Valid, spacy.load(Output_model + "model_spacy/small/test1.model")
    )

    # Evaluate without rules
    evaluator.evaluate_without_rules()
    print("\n")

    # Evaluate with rules
    evaluator.evaluate_with_rules()


if __name__ == "__main__":
    main()
