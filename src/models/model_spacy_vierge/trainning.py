""" Train a Named Entity Recognition (NER) model using spaCy """

import ast
import random
from tqdm import tqdm
from langcodes import Language
import spacy
import pandas as pd
from datetime import datetime
from spacy.training import Example

from typing import List, Optional, Tuple
from config import Output_model, Train_vierge, Valid_vierge
from src.models.trainning_parent import Trainner
from src.models.model_spacy_vierge.evaluate import evaluate_model


class SpacyNERTrainer_vierge(Trainner):
    """
    A class to train a Named Entity Recognition (NER) model using spaCy.
    """

    def __init__(self) -> None:
        """Initializes the SpacyNERTrainer_vierge class."""
        self.nlp: Optional[Language] = spacy.blank("fr")
        if "ner" not in self.nlp.pipe_names:
            self.ner = self.nlp.add_pipe("ner")
        else:
            self.ner = self.nlp.get_pipe("ner")

        self.train_data: List[Tuple[str, dict]] = []
        self.valid_data: List[Tuple[str, dict]] = []

        self.ner.add_label("DEPART")
        self.ner.add_label("CORRESPONDANCE")
        self.ner.add_label("ARRIVEE")
        self.model_size: str = "vierge"

    def load_data(self, train_file: str, train=True) -> List[Tuple[str, dict]]:
        """
        Loads the training data from CSV files and transforms it into a list of tuples.

        Parameters:
        -----------
        train_file : str
            Path to the training data CSV file.

        Returns:
        --------
        self.train_data : List[Tuple[str, dict]]
        """
        df_data: pd.DataFrame = pd.read_csv(train_file)

        if not {"Phrase", "Reponse"}.issubset(df_data.columns):
            raise ValueError(
                "Le fichier CSV doit contenir les colonnes 'Phrase' et 'Reponse'."
            )

        for _, row in df_data.iterrows():
            phrase = row["Phrase"]
            annotations = ast.literal_eval(row["Reponse"])
            if not isinstance(annotations, dict) or "entities" not in annotations:
                raise ValueError(
                    f"Annotation invalide pour la phrase '{phrase}': {annotations}"
                )

            if train:
                self.train_data.append((phrase, annotations))
            else:
                self.valid_data.append((phrase, annotations))

        if train:
            return self.train_data
        else:
            return self.valid_data

    def has_overlapping_entities(self, entities):
        for i, (start_i, end_i, _) in enumerate(entities):
            for j, (start_j, end_j, _) in enumerate(entities):
                if i != j and not (end_i <= start_j or start_i >= end_j):
                    return True
        return False

    def train_spacy(
        self, iterations: int = 100, batch_size: int = 20, patience: int = 20
    ) -> spacy.language.Language:
        """
        Train the SpaCy NER model with a blank pipeline using the loaded training data.

        Parameters:
        -----------
        iterations : int
            The number of training iterations.
        batch_size : int
            The number of examples to include in each training batch.
        """
        best_loss: float = float("inf")
        best_model: spacy.language.Language = None
        losses_per_iteration: list = []

        no_improvement_count = 0

        examples = []
        for text, annotations in self.train_data:
            doc = self.nlp.make_doc(text)
            if not self.has_overlapping_entities(annotations["entities"]):
                example = Example.from_dict(doc, annotations)
                examples.append(example)
            else:
                print(f"Skipping text due to overlapping entities: {text}")

        for itn in range(iterations):
            random.shuffle(examples)
            losses = {}
            for batch in spacy.util.minibatch(examples, size=batch_size):
                self.nlp.update(batch, drop=0.05, losses=losses)

            current_loss = losses.get("ner", float("inf"))
            losses_per_iteration.append(current_loss)
            if current_loss < best_loss:
                best_loss = current_loss
                best_model = self.nlp
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            if no_improvement_count >= patience:
                print(f"Early stopping triggered after {itn + 1} iterations.")
                break

        self.plot_losses(losses_per_iteration)

        return best_model, best_loss


if __name__ == "__main__":

    trainer = SpacyNERTrainer_vierge()
    valid = trainer.load_data(train_file=Valid_vierge, train=False)
    trainer.load_data(train_file=Train_vierge)

    date_today = datetime.today().strftime("%Y-%m-%d")
    output_dir = Output_model + f"/{date_today}_trained.model"

    optimizer = trainer.nlp.begin_training()

    best_model = None
    best_loss = float("inf")
    best_accurancy = 0.0 

    for epoch in tqdm(range(10), desc="Training epochs", unit="epoch"):
        model, loss = trainer.train_spacy(iterations=100, batch_size=50)
        accurancy = evaluate_model(model, valid)

        tqdm.write(f"[Epoch {epoch + 1}] Loss: {loss:.4f}, Accuracy: {accurancy:.4f}")
        if accurancy > best_accurancy:
            best_model = model
            best_loss = loss
            best_accurancy = accurancy

    trainer.save_model(model_to_save=best_model, output_dir=output_dir)
    print(f"Best loss: {best_loss}")
    print(f"Best accurancy: {best_accurancy}")
