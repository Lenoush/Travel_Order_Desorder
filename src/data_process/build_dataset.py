from utils import (
    write_data_to_csv,
    load_sncf_data,
    replace_and_generate_response,
    merge_datasets,
    replace_and_generate_error,
    load_data,
)
from data.data_need import (
    data_actif_without,
    data_actif_with,
    data_passif,
    data_question,
    data_error,
    data_direct,
    data_unique,
)
from config import Dataset, Train, Test, Valid

import pandas as pd
from sklearn.model_selection import train_test_split


def build() -> None:
    """
    Writes the example sentences dataset to a CSV file.
    """
    processed_actif = replace_and_generate_response(data_actif_with * 10)
    processed_actif = replace_and_generate_response(data_actif_without)
    processed_passif = replace_and_generate_response(data_passif)
    processed_question = replace_and_generate_response(data_question)
    processed_direct = replace_and_generate_response(data_direct * 50)
    processed_error = replace_and_generate_error(data_error)

    merged_data = merge_datasets(
        processed_actif,
        processed_passif,
        processed_question,
        processed_error,
        processed_direct,
    )

    write_data_to_csv(merged_data, Dataset)


class BuildDataset:
    """
    A class to load and build a dataset from SNCF data and write it to a CSV file.
    """

    def __init__(self, dataset_path: str, random_state: int = 42) -> None:
        """
        Initializes the BuildDataset class by loading the SNCF data.
        """
        self.data: pd.DataFrame = load_sncf_data()
        self.dataset_path: str = dataset_path
        self.random_state: int = random_state
        self.X_train: list[str] = []
        self.X_val: list[str] = []
        self.X_test: list[str] = []
        self.y_train: list[str] = []
        self.y_val: list[str] = []
        self.y_test: list[str] = []

    def build_unique(self) -> None:
        """
        Processes the unique dataset sentences and splits them equally between validation and test sets.
        """
        processed_unique = replace_and_generate_response(data_unique)
        processed_direct_train = replace_and_generate_response(data_direct * 50)

        unique_val, unique_test = train_test_split(
            processed_unique + processed_direct_train,
            test_size=0.5,
            random_state=self.random_state,
        )

        self.X_val.extend([item[0] for item in unique_val])
        self.y_val.extend([item[1] for item in unique_val])
        self.X_test.extend([item[0] for item in unique_test])
        self.y_test.extend([item[1] for item in unique_test])

    def split_data(self, input_phrases: list[str], responses: list[str]) -> None:
        """
        Splits the dataset into training, validation, and test sets with a 70-15-15 ratio.
        """
        # Split into training (70%) and test+validation (30%)
        self.X_train, x_test, self.y_train, y_test = train_test_split(
            input_phrases, responses, test_size=0.3, random_state=self.random_state
        )
        # Split test+validation (15% each)
        x_val, x_test, y_val, y_test = train_test_split(
            x_test, y_test, test_size=0.5, random_state=self.random_state
        )

        self.X_val.extend(x_val)
        self.y_val.extend(y_val)
        self.X_test.extend(x_test)
        self.y_test.extend(y_test)

    def save_data(
        self,
        train_file: str = Train,
        val_file: str = Valid,
        test_file: str = Test,
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

        # Helper function to save data to a CSV
        def save_to_csv(data: list[str], labels: list[str], filename: str) -> None:
            pd.DataFrame({"Phrase": data, "Reponse": labels}).to_csv(
                filename, index=False
            )

        save_to_csv(self.X_train, self.y_train, train_file)
        save_to_csv(self.X_val, self.y_val, val_file)
        save_to_csv(self.X_test, self.y_test, test_file)


if __name__ == "__main__":
    dataset = BuildDataset(dataset_path=Dataset)
    build()
    phrases, responses = load_data(dataset.dataset_path)
    dataset.split_data(phrases, responses)
    dataset.build_unique()
    dataset.save_data()
