from datetime import datetime
import spacy
import pandas as pd
import sys
from spacy.util import minibatch
from spacy.training import Example

from typing import List, Tuple
from config import Output_model, Train_train

from src.models.trainning_parent import Trainner


class SpacyNERTrainer(Trainner):
    """
    A class to train a Named Entity Recognition (NER) model using spaCy.
    """

    def __init__(self, model_size: str) -> None:
        """Initializes the SpacyNERTrainer class.

        Parameters:
        -----------
        model_size : str
            The size of the spaCy model to use. Must be either 'small', 'medium' or 'large'.
        """
        model_map: dict = {
            "small": "fr_core_news_sm",
            "medium": "fr_core_news_md",
            "large": "fr_core_news_lg",
        }

        self.model_size: str = model_size
        self.train_data: List[Tuple[str, dict]] = []
        self.nlp: spacy.language.Language = spacy.load(model_map[model_size])
        self.ner = self.nlp.get_pipe("ner")

    def load_data(self, train_file: str) -> List[Tuple[str, dict]]:
        df_train: pd.DataFrame = pd.read_csv(train_file)

        X_train: List[str] = df_train["Phrase"].to_list()
        y_train: List[str] = df_train["Reponse"].to_list()

        for phrase, response in zip(X_train, y_train):
            entities: List[Tuple[int, int, str]] = []
            seen_spans = set()

            for ent in response.split(":"):
                start_char = phrase.find(ent)
                end_char = start_char + len(ent)

                if start_char != -1:
                    # Check for overlaps
                    if any(s < end_char and start_char < e for s, e in seen_spans):
                        continue  # Skip overlapping entities
                    entities.append((start_char, end_char, "LOC"))
                    seen_spans.add((start_char, end_char))

            self.train_data.append((phrase, {"entities": entities}))

        return self.train_data

    def train_spacy(
        self, Train_data: List[Tuple[str, dict]], iterations: int = 100
    ) -> spacy.language.Language:
        """
        Trains the NER model on the prepared training data.

        Parameters:
        -----------
        iterations : int
            The number of training iterations (default is 100).
        Train_data : List[Tuple[str, dict]]
            The training data in the format of a list of tuples, where each tuple contains a text and its annotations.

        Returns:
        --------
        spacy.language.Language
            The trained spaCy model.
        """
        best_loss: float = float("inf")
        best_model: spacy.language.Language = None
        losses_per_iteration: list = []

        for _, annotations in Train_data:
            for ent in annotations.get("entities"):
                self.ner.add_label(ent[2])

        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.resume_training()
            for i in range(iterations):
                losses = {}
                batches = minibatch(
                    Train_data, size=100
                )  # compounding(5.0, 32.0, 1.0214)
                for batch in batches:
                    texts, annotations = zip(*batch)
                    for text, annot in zip(texts, annotations):
                        doc = self.nlp.make_doc(text)
                        try:
                            example = Example.from_dict(doc, annot)

                            conflicting_entities = []
                            seen = set()
                            for start, end, label in annot["entities"]:
                                if any(s < end and start < e for s, e, _ in seen):
                                    conflicting_entities.append((start, end, label))
                                else:
                                    seen.add((start, end, label))
                            if conflicting_entities:
                                print(
                                    f"Conflits détectés pour '{text}': {conflicting_entities}"
                                )
                                continue

                            self.nlp.update(
                                [example], drop=0.1, sgd=optimizer, losses=losses
                            )
                        except Exception as e:
                            print(f"Error: {e}")
                            pass
                print(f"Iteration {i + 1}, Losses: {losses}")

                current_loss = sum(losses.values())
                losses_per_iteration.append(current_loss)
                if current_loss < best_loss:
                    best_loss = current_loss
                    best_model = self.nlp

        self.plot_losses(losses_per_iteration)

        return best_model


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python trainning.py <model_size>")
        print("model_size: 'small' , 'medium' or 'large'")
        sys.exit(1)
    else:
        if sys.argv[1] not in ["small", "medium", "large"]:
            print("model_size: 'small' , 'medium' or 'large'")
            sys.exit(1)
        else:
            model_size = sys.argv[1]
            trainer = SpacyNERTrainer(model_size=model_size)
            train = trainer.load_data(train_file=Train_train)

            date_today = datetime.today().strftime("%Y-%m-%d")
            output_dir = Output_model + f"model_spacy/{model_size}_trained.model"

            trained_model = trainer.train_spacy(train, iterations=100)
            trainer.save_model(model_to_save=trained_model, output_dir=output_dir)
