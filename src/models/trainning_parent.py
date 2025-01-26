from typing import List
from matplotlib import pyplot as plt
import spacy
from config import Output_model
from datetime import datetime


class Trainner:
    """
    A class parent to train a model
    """

    def __init__(self):
        pass

    def save_model(
        self, model_to_save: spacy.language.Language, output_dir: str
    ) -> None:
        """
        Saves the trained model to the specified directory.

        Parameters:
        -----------
        output_dir : str
            The directory where the model will be saved.
        """
        model_to_save.to_disk(output_dir)
        print(f"Model saved to {output_dir}")

    def plot_losses(self, losses_per_iteration: List[float]) -> None:
        """
        Saves a plot of the losses per iteration to the specified directory.

        Parameters:
        -----------
        losses_per_iteration : List[float]
            List of losses calculated at each training iteration.
        output_dir : str
            The directory where the plot will be saved.
        """
        plt.figure(figsize=(10, 6))
        plt.plot(
            range(1, len(losses_per_iteration) + 1),
            losses_per_iteration,
            marker="o",
            color="b",
            label="Loss",
        )
        plt.title("Loss per Iteration")
        plt.xlabel("Iteration")
        plt.ylabel("Loss")
        plt.legend()
        plt.grid(True)

        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.model_size == "vierge":
            output_path = (
            Output_model + f"model_spacy_vierge/{self.model_size}_train_losses_{current_date}.png"
            )
        else:
            output_path = (
            Output_model + f"model_spacy/{self.model_size}_train_losses.png"
            )
        plt.savefig(output_path)
        plt.close()
        print(f"Loss plot saved to {output_path}")
