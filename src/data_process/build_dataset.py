"""  This script is used to build the dataset for training the model."""

import sys
from typing import List, Tuple
import pandas as pd
from sklearn.model_selection import train_test_split

from src.data_process.utils import (
    write_data_to_csv,
    merge_datasets,
    load_data,
    load_sncf_data,
    RGR_train,
    RGR_vierge,
)
from data.data_need import (
    data_actif_without,
    data_actif_with,
    data_question,
    data_direct,
    data_unique,
)
from config import (
    Dataset_train,
    Train_train,
    Test_train,
    Valid_train,
    Dataset_vierge,
    Train_vierge,
    Test_vierge,
    Valid_vierge,
)


class BuildDataset:
    """
    A class to load and build a dataset from SNCF data and write it to a CSV file.
    """

    def __init__(
        self,
        dataset_path: str,
        random_state: int = 42,
        vierge: bool = False,
        train_file: str = Train_train,
        val_file: str = Valid_train,
        test_file: str = Test_train,
    ) -> None:
        """
        Initializes the BuildDataset class by loading the SNCF data, setting the dataset path and creating lists to store the split data.
        """
        self.data: pd.DataFrame = load_sncf_data()
        self.dataset_path: str = dataset_path
        self.train_file: str = train_file
        self.val_file: str = val_file
        self.test_file: str = test_file

        self.random_state: int = random_state
        self.vierge: bool = vierge

        self.X_train: list[str] = []
        self.X_val: list[str] = []
        self.X_test: list[str] = []
        self.y_train: list[str] = []
        self.y_val: list[str] = []
        self.y_test: list[str] = []

    def build(self) -> None:
        """
        Builds the dataset by processing the example sentences and writing them to a CSV file.
        """
        if self.vierge:
            processed_actif: List[Tuple[str, dict]] = RGR_vierge(data_actif_with)
            processed_actif_without: List[Tuple[str, dict]] = RGR_vierge(
                data_actif_without
            )
            processed_question: List[Tuple[str, dict]] = RGR_vierge(data_question)
            processed_direct: List[Tuple[str, dict]] = RGR_vierge(data_direct)
            # processed_error:List[Tuple[str, dict]] = RGE_vierge(data_error)
        else:
            processed_actif: List[Tuple[str, dict]] = RGR_train(data_actif_with)
            processed_actif_without: List[Tuple[str, dict]] = RGR_train(
                data_actif_without
            )
            processed_question: List[Tuple[str, dict]] = RGR_train(data_question)
            processed_direct: List[Tuple[str, dict]] = RGR_train(data_direct)
            # processed_error:List[Tuple[str, dict]] = RGE_train(data_error)

        merged_data: List[str] = merge_datasets(
            processed_actif,
            processed_question,
            processed_actif_without,
            # processed_error,
            processed_direct,
        )

        write_data_to_csv(merged_data, self.dataset_path)

    def build_unique(self) -> None:
        """
        Builds the unique dataset by processing the example sentences and splitting them into validation and test sets.
        We will not have this kind of sentence in the training set.
        """
        if self.vierge:
            processed_unique: List[Tuple[str, dict]] = RGR_vierge(data_unique)
            processed_direct_train: List[Tuple[str, dict]] = RGR_vierge(data_direct)
        else:
            processed_unique: List[Tuple[str, dict]] = RGR_train(data_unique)
            processed_direct_train: List[Tuple[str, dict]] = RGR_train(data_direct)

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

    def save_data(self) -> None:
        """
        Saves the split data into separate CSV files for training, validation, and test sets.
        """

        def save_to_csv(dataX: list[str], dataY: list[str], filename: str) -> None:
            pd.DataFrame({"Phrase": dataX, "Reponse": dataY}).to_csv(
                filename, index=False
            )

        save_to_csv(self.X_train, self.y_train, self.train_file)
        save_to_csv(self.X_val, self.y_val, self.val_file)
        save_to_csv(self.X_test, self.y_test, self.test_file)


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            print("Usage: python build_dataset.py <vierge or train>")
            sys.exit(1)
        else:
            if sys.argv[1] == "vierge":
                dataset = BuildDataset(
                    dataset_path=Dataset_vierge,
                    vierge=True,
                    train_file=Train_vierge,
                    val_file=Valid_vierge,
                    test_file=Test_vierge,
                )
            elif sys.argv[1] == "train":
                dataset = BuildDataset(dataset_path=Dataset_train)
            else:
                print("Usage: python build_dataset.py <vierge or train>")
                sys.exit(1)
    except (ValueError, TypeError):
        print("Usage: python build_dataset.py <vierge or train>")
        sys.exit(1)

    print("Building dataset")
    dataset.build()
    print("Loading and splitting data")
    phrases, responses = load_data(dataset.dataset_path)
    dataset.split_data(phrases, responses)
    print("Building unique dataset")
    dataset.build_unique()
    print("Saving data")
    dataset.save_data()
