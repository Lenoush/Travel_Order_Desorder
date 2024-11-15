import spacy
import pandas as pd
import sys
from spacy.util import minibatch, compounding
from spacy.training import Example
from spacy.scorer import Scorer
from typing import List, Tuple
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

    def __init__(self, model_size: str):
        model_map = {
            "small": "fr_core_news_sm",
            "medium": "fr_core_news_md",
            "large": "fr_core_news_lg",
        }
        if model_size not in model_map:
            raise ValueError("Model size must be either 'small', 'medium' or 'large'")

        self.model_size = model_size
        self.train_data = []
        self.nlp: spacy.language.Language = spacy.load(model_map[model_size])
        self.ner = self.nlp.get_pipe("ner")

    def load_data(self, train_file: str) -> None:
        """
        Loads the training data from CSV files.

        Parameters:
        -----------
        train_file : str
            Path to the training data CSV file.
        """
        df_train: pd.DataFrame = pd.read_csv(train_file)

        X_train: List[str] = df_train["Phrase"].to_list()
        y_train: List[str] = df_train["Reponse"].to_list()

        for phrase, response in zip(X_train, y_train):
            entities: List[Tuple[int, int, str]] = []
            for ent in response.split(":"):
                start_char = phrase.find(ent)
                end_char = start_char + len(ent)
                if start_char != -1:
                    entities.append((start_char, end_char, "LOC"))
            self.train_data.append((phrase, {"entities": entities}))

        return self.train_data

    def evaluate(self, eval_data):
        """Evaluate the model on a validation dataset."""
        scorer = Scorer()
        examples = [
            Example.from_dict(self.nlp.make_doc(text), annot)
            for text, annot in eval_data
        ]
        for example in examples:
            self.nlp(example.predicted)
            scorer.score(example)
        return scorer.scores

    def train_spacy(self, Train_data, iterations: int = 100) -> spacy.language.Language:
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
        best_loss = float("inf")
        best_model = None

        for _, annotations in Train_data:
            for ent in annotations.get("entities"):
                self.ner.add_label(ent[2])

        # Disable other components of the pipeline to train only the NER
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.resume_training()
            for i in range(iterations):
                losses = {}
                batches = minibatch(Train_data, size=compounding(5.0, 32.0, 1.0214))
                for batch in batches:
                    texts, annotations = zip(*batch)
                    for text, annot in zip(texts, annotations):
                        doc = self.nlp.make_doc(text)
                        try:
                            example = Example.from_dict(doc, annot)
                            self.nlp.update(
                                [example], drop=0.1, sgd=optimizer, losses=losses
                            )
                        except Exception as e:
                            print(f"Error: {e}")
                            pass
                print(f"Iteration {i + 1}, Losses: {losses}")

                # Check if the current loss is the best
                current_loss = sum(losses.values())
                if current_loss < best_loss:
                    best_loss = current_loss
                    best_model = self.nlp  # Save the best model

        return best_model

    def save_model(self, model_to_save, output_dir: str) -> None:
        """
        Saves the trained model to the specified directory.

        Parameters:
        -----------
        output_dir : str
            The directory where the model will be saved.
        """
        model_to_save.to_disk(output_dir)
        print(f"Model saved to {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python trainning.py <model_size>")
        print("model_size: 'small' , 'medium' or 'large'")
        sys.exit(1)

    model_size = sys.argv[1]
    trainer = SpacyNERTrainer(model_size=model_size)
    train = trainer.load_data(train_file=Train)

    output_dir = Output_model + f"model_spacy/small/{model_size}_trained.model"
    trained_model = trainer.train_spacy(train, iterations=100)
    trainer.save_model(model_to_save=trained_model, output_dir=output_dir)
