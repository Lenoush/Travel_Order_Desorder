import spacy
import pandas as pd
from typing import List
from config import Valid


class EntityEvaluator:
    """
    Class to evaluate named entity recognition (NER) using SpaCy, with options for applying custom rules.
    """

    def __init__(self, phrases: List[str], responses: List[str]):
        """
        Initializes the EntityEvaluator.
        """
        self.phrases = phrases
        self.responses = responses
        self.model = spacy.load("fr_core_news_sm")
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

    def is_first_name(self, phrase: str) -> bool:
        """
        Determines if the given phrase contains a first name.
        """
        doc = self.model(phrase)
        for index in range(1, len(doc)):
            if doc[index].label_ == "LOC" and doc[index - 1].text in [
                "s'appelle",
                "appelle",
                "nomme",
                "surmonme",
            ]:
                return True
        return False

    def has_less_than_2_locs(self, phrase: str) -> bool:
        """
        Determines if the given phrase contains less than 2 LOC entities.
        """
        doc = self.model(phrase)
        return len([ent for ent in doc.ents if ent.label_ == "LOC"]) < 2

    def is_LOC_egal_RER(self, ent) -> bool:
        """
        Determines if the given entity is a LOC entity and contains "RER".
        """
        return ent.label_ == "LOC" and "RER" in ent.text

    def evaluate_without_rules(self) -> None:
        """
        Evaluates entity recognition without using any custom rules.
        """
        correct = 0
        total = len(self.phrases)

        for phrase, response in zip(self.phrases, self.responses):
            doc = self.model(phrase)
            all_LOC = [ent.text for ent in doc.ents if ent.label_ == "LOC"]

            if response == "Error":
                if len(all_LOC) < 2:
                    correct += 1
            else:
                expected = response.split(":")
                if len(all_LOC) == len(expected):
                    if all(loc in expected for loc in all_LOC):
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

        for phrase, response in zip(self.phrases, self.responses):
            lemmatized_phrase = self.lemmatize_phrase(phrase)
            doc = self.model(lemmatized_phrase)
            all_LOC = [ent for ent in doc.ents if ent.label_ == "LOC"]

            # Appliquer les règles
            if self.has_less_than_2_locs(lemmatized_phrase):
                all_LOC = []  # On considère qu'il n'y a pas d'entités valides

            # Modifier l'étiquette si l'entité est un RER
            all_LOC = [ent for ent in all_LOC if not self.is_LOC_egal_RER(ent)]

            if response == "Error":
                if len(all_LOC) < 2:
                    correct += 1
            else:
                expected = response.split(":")
                if len(all_LOC) == len(expected):
                    if all(loc in expected for loc in all_LOC):
                        correct += 1

        accuracy = (correct / total) * 100
        print("With rules")
        print(f"Accuracy: {accuracy:.2f}%")


def main():
    # Read data from CSV
    df = pd.read_csv(Valid)
    phrases = df["Phrase"].tolist()
    responses = df["Reponse"].tolist()

    # Initialize evaluator
    evaluator = EntityEvaluator(phrases, responses)

    # Evaluate without rules
    evaluator.evaluate_without_rules()
    print("\n")

    # Evaluate with rules
    evaluator.evaluate_with_rules()


if __name__ == "__main__":
    main()
