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
        self.good = 0
        self.bad = 0
        self.corriger = 0
        self.symbols = ["-", "'", "`", "`", "‘", "’", "'", "´", "ˋ"]

    def lemmatize_phrase(self, phrase: str) -> str:
        """
        Lemmatizes the input phrase.

        Args:
            phrase (str): Input phrase to lemmatize.

        Returns:
            str: Lemmatized phrase.
        """
        doc = self.model(phrase)
        lemmatized = []

        for token in doc:
            if token.pos_ == "VERB":
                lemmatized.append(f" {token.lemma_} ")
            elif token.text in self.symbols:
                lemmatized.append(token.text)
            elif len(lemmatized) > 0 and lemmatized[-1] in self.symbols:
                lemmatized.append(f"{token.text}")
            else:
                lemmatized.append(f" {token.text}")

        return "".join(lemmatized).strip()

    def est_une_question(self, phrase: str) -> bool:
        """
        Determines if the given phrase is a question.

        Args:
            phrase (str): Input phrase.

        Returns:
            bool: True if the phrase is a question, otherwise False.
        """
        doc = self.model(phrase)
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
        return any(token.lemma_ in mots_interrogatifs or "?" in phrase for token in doc)

    def evaluate_without_rules(self) -> None:
        """
        Evaluates entity recognition without using any custom rules.
        """
        self.good = 0
        self.bad = 0

        for phrase, response in zip(self.phrases, self.responses):
            doc = self.model(phrase)
            for ent in doc.ents:
                if ent.label_ == "LOC" and ent.text in response:
                    self.good += 1
                elif ent.label_ == "LOC" and ent.text not in response:
                    self.bad += 1

        total = len(self.phrases)
        print("Without rules")
        print(f"Correct: {(self.good / total) * 100:.2f}%")
        print(f"Incorrect: {(self.bad / total) * 100:.2f}%")

    def evaluate_with_rules(self) -> None:
        """
        Evaluates entity recognition with custom rules.
        """
        self.good = 0
        self.bad = 0
        self.corriger = 0
        lemmatized_phrases = []

        for phrase, response in zip(self.phrases, self.responses):
            doc = self.model(phrase)
            lemmatized_phrase = self.lemmatize_phrase(phrase)
            lemmatized_phrases.append(lemmatized_phrase)
            list_phrase = lemmatized_phrase.split()

            for ent in doc.ents:
                if ent.label_ == "LOC" and ent.text not in response:
                    try:
                        index = list_phrase.index(ent.text)

                        # Check preceding word for exclusion criteria
                        if index > 0 and list_phrase[index - 1] in [
                            "nommer",
                            "appeler",
                            "surmonmer",
                            "s'appeler",
                        ]:
                            ent.label_ = "OTHER"
                            self.corriger += 1
                            continue

                        # Exclude if the entity contains "RER"
                        if "RER" in ent.text:
                            ent.label_ = "OTHER"
                            self.corriger += 1
                            continue

                        # Exclude if the phrase is a question
                        if self.est_une_question(phrase):
                            ent.label_ = "OTHER"
                            self.corriger += 1
                            continue

                        # Exclude if there's only one LOC in the phrase
                        if len([e for e in doc.ents if e.label_ == "LOC"]) == 1:
                            ent.label_ = "OTHER"
                            self.corriger += 1
                            continue

                        self.bad += 1  # Entity is not considered valid
                    except ValueError:
                        self.bad += 1
                elif ent.label_ == "LOC" and ent.text in response:
                    self.good += 1

        total = self.good + self.bad
        print("With rules")
        print(f"Correct: {(self.good / total) * 100:.2f}%")
        print(f"Corrected: {(self.corriger / total) * 100:.2f}%")
        print(f"Incorrect: {(self.bad / total) * 100:.2f}%")


def main():
    # Read data from CSV
    df = pd.read_csv(Valid)
    phrases = df["Phrase"].tolist()
    responses = df["Reponse"].tolist()

    # Initialize evaluator
    evaluator = EntityEvaluator(phrases, responses)

    # Evaluate without rules
    evaluator.evaluate_without_rules()

    # Evaluate with rules
    evaluator.evaluate_with_rules()


if __name__ == "__main__":
    main()
