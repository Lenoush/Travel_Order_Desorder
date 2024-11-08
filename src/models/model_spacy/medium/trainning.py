import os
import sys

import spacy
import pandas as pd
from spacy.util import minibatch, compounding
from spacy.training import Example
from typing import List, Tuple, Dict
from config import Output_model, Train


class SpacyNERTrainer:
    """
    A class to train a Named Entity Recognition (NER) model using spaCy.

    Attributes:
    -----------
    train_data : List[Tuple[str, Dict[str, List[Tuple[int, int, str]]]]]
        The training data consisting of phrases and their associated entities.
    nlp : spacy.language.Language
        The spaCy language model.

    Methods:
    --------
    load_data(train_file: str) -> None:
        Loads the training data from CSV files.

    prepare_data() -> None:
        Prepares the training data for the NER model.

    train_spacy(iterations: int = 100) -> spacy.language.Language:
        Trains the NER model on the prepared training data.

    save_model(output_dir: str) -> None:
        Saves the trained model to the specified directory.
    """

    def __init__(self):
        self.train_data: List[Tuple[str, Dict[str, List[Tuple[int, int, str]]]]] = []
        self.nlp: spacy.language.Language = spacy.load("fr_core_news_md")
        self.ner = self.nlp.get_pipe("ner")

    def load_data(self, train_file: str) -> None:
        """
        Loads the training data from CSV files.

        Parameters:
        -----------
        train_file : str
            Path to the training data CSV file.
        """
        print(f"Loading training data from {train_file}")
        df_train: pd.DataFrame = pd.read_csv(train_file)

        X_train: List[str] = df_train["Phrase"].to_list()
        y_train: List[str] = df_train["Reponse"].to_list()

        for phrase, response in zip(X_train, y_train):
            entities: List[Tuple[int, int, str]] = []
            for ent in response.split(":"):
                start_char = phrase.find(ent)
                end_char = start_char + len(ent)
                if start_char != -1:
                    entities.append((start_char, end_char, ent))
                else:
                    entities.append((0, 0, ent))
            self.train_data.append((phrase, {"entities": entities}))

        print(f"Loaded {len(self.train_data)} training examples")

        return self.train_data

    def train_spacy(self, iterations: int = 100) -> spacy.language.Language:
        """
        Trains the NER model on the prepared training data.

        Parameters:
        -----------
        iterations : int
            The number of training iterations (default is 100).

        Returns:
        --------
        spacy.language.Language
            The trained spaCy model.
        """
        print("Training the NER model")
        for _, annotations in self.train_data:
            print(annotations.get("entities"))
            for ent in annotations.get("entities"):
                print(ent[2])
                self.ner.add_label(ent[2])

        # Disable other components of the pipeline to train only the NER
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.begin_training()
            for i in range(iterations):
                losses = {}
                batches = minibatch(self.train_data, size=compounding(4.0, 32.0, 1.001))
                for batch in batches:
                    texts, annotations = zip(*batch)
                    for text, annot in zip(texts, annotations):
                        doc = self.nlp.make_doc(text)
                        example = Example.from_dict(doc, annot)
                        self.nlp.update(
                            [example], drop=0.1, sgd=optimizer, losses=losses
                        )
                print(f"Iteration {i + 1}, Losses: {losses}")

        return self.nlp

    def save_model(self, output_dir: str) -> None:
        """
        Saves the trained model to the specified directory.

        Parameters:
        -----------
        output_dir : str
            The directory where the model will be saved.
        """
        self.nlp.to_disk(output_dir)
        print(f"Model saved to {output_dir}")


if __name__ == "__main__":
    trainer = SpacyNERTrainer()
    trainer.load_data(train_file="../../" + Train)
    trained_model = trainer.train_spacy(iterations=100)
    trainer.save_model(output_dir=Output_model + "medium/" + "test1.model")
