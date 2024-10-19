import pandas as pd
from sklearn.model_selection import train_test_split


class DatasetSplitter:
    """
    A class to split a dataset into training, validation, and test sets and save them as CSV files.

    Attributes:
    -----------
    dataset_path : str
        Path to the dataset file.
    random_state : int
        Seed to control the randomization of the data splitting.

    Methods:
    --------
    load_data() -> None:
        Loads the dataset and extracts the 'Phrase' and 'Reponse' columns.

    split_data() -> None:
        Splits the dataset into training, validation, and test sets with a 70-15-15 ratio.

    save_data(train_file: str, val_file: str, test_file: str) -> None:
        Saves the split data into separate CSV files for training, validation, and test sets.
    """

    def __init__(self, dataset_path: str, random_state: int = 42) -> None:
        """
        Initializes the DatasetSplitter with the dataset path and random state.

        Parameters:
        -----------
        dataset_path : str
            Path to the dataset file.
        random_state : int, optional
            Seed to control the randomization of data splitting (default is 42).
        """
        self.dataset_path: str = dataset_path
        self.random_state: int = random_state
        self.phrases: list[str] = []
        self.responses: list[str] = []
        self.X_train: list[str] = []
        self.X_val: list[str] = []
        self.X_test: list[str] = []
        self.y_train: list[str] = []
        self.y_val: list[str] = []
        self.y_test: list[str] = []

    def load_data(self) -> None:
        """
        Loads the dataset from the specified path and extracts the 'Phrase' and 'Reponse' columns.
        """
        df: pd.DataFrame = pd.read_csv(self.dataset_path)
        self.phrases = df["Phrase"].tolist()
        self.responses = df["Reponse"].tolist()

    def split_data(self) -> None:
        """
        Splits the dataset into training, validation, and test sets with a 70-15-15 ratio.
        """
        # Split into training (70%) and test+validation (30%)
        self.X_train, X_test, self.y_train, y_test = train_test_split(
            self.phrases, self.responses, test_size=0.3, random_state=self.random_state
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
        X_train_df: pd.DataFrame = pd.DataFrame(self.X_train, columns=["Phrase"])
        X_train_df["Reponse"] = self.y_train
        X_train_df.to_csv(train_file, index=False)

        # Save validation set
        X_val_df: pd.DataFrame = pd.DataFrame(self.X_val, columns=["Phrase"])
        X_val_df["Reponse"] = self.y_val
        X_val_df.to_csv(val_file, index=False)

        # Save test set
        X_test_df: pd.DataFrame = pd.DataFrame(self.X_test, columns=["Phrase"])
        X_test_df["Reponse"] = self.y_test
        X_test_df.to_csv(test_file, index=False)


if __name__ == "__main__":
    dataset = DatasetSplitter(dataset_path="data/dataset.csv")
    dataset.load_data()
    dataset.split_data()
    dataset.save_data()
