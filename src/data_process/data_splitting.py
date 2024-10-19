import pandas as pd
from sklearn.model_selection import train_test_split
from utils import load_data


class DatasetSplitter:
    """
    A class to split a dataset into training, validation, and test sets and save them as CSV files.
    """

    def __init__(self, dataset_path: str, random_state: int = 42) -> None:
        """
        Initializes the DatasetSplitter with the dataset path and random state.
        """
        self.dataset_path: str = dataset_path
        self.random_state: int = random_state
        self.X_train: list[str] = []
        self.X_val: list[str] = []
        self.X_test: list[str] = []
        self.y_train: list[str] = []
        self.y_val: list[str] = []
        self.y_test: list[str] = []

    def split_data(self, phrases: list[str], responses: list[str]) -> None:
        """
        Splits the dataset into training, validation, and test sets with a 70-15-15 ratio.
        """
        # Split into training (70%) and test+validation (30%)
        self.X_train, X_test, self.y_train, y_test = train_test_split(
            phrases, responses, test_size=0.3, random_state=self.random_state
        )
        # Split test+validation (15% each)
        self.X_val, self.X_test, self.y_val, self.y_test = train_test_split(
            X_test, y_test, test_size=0.5, random_state=self.random_state
        )

    def save_data(
        self,
        train_file: str = "data/train_dataset.csv",
        val_file: str = "data/valid_dataset.csv",
        test_file: str = "data/test_dataset.csv",
    ) -> None:
        """
        Saves the split data into separate CSV files for training, validation, and test sets.

        Parameters:
        -----------
        train_file : str, optional
            Path to save the training data (default is 'data/train_dataset.csv').
        val_file : str, optional
            Path to save the validation data (default is 'data/valid_dataset.csv').
        test_file : str, optional
            Path to save the test data (default is 'data/test_dataset.csv').
        """
        # Save training set
        X_train_df = pd.DataFrame({"Phrase": self.X_train, "Reponse": self.y_train})
        X_train_df.to_csv(train_file, index=False)

        # Save validation set
        X_val_df = pd.DataFrame({"Phrase": self.X_val, "Reponse": self.y_val})
        X_val_df.to_csv(val_file, index=False)

        # Save test set
        X_test_df = pd.DataFrame({"Phrase": self.X_test, "Reponse": self.y_test})
        X_test_df.to_csv(test_file, index=False)


if __name__ == "__main__":
    dataset = DatasetSplitter(dataset_path="data/dataset.csv")
    phrases, responses = load_data(dataset.dataset_path)
    dataset.split_data(phrases, responses)
    dataset.save_data()
