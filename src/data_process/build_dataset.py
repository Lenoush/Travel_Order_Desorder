from utils import (
    write_data_to_csv,
    load_sncf_data,
    replace_and_generate_response,
    merge_datasets,
    replace_and_generate_error,
)
from data.example_sentences import data_actif, data_passif, data_question, data_error
from config import Dataset


class BuildDataset:
    """
    A class to load and build a dataset from SNCF data and write it to a CSV file.
    """

    def __init__(self) -> None:
        """
        Initializes the BuildDataset class by loading the SNCF data.
        """
        self.data: list = load_sncf_data()

    def build(self) -> None:
        """
        Writes the example sentences dataset to a CSV file.
        """
        processed_actif = replace_and_generate_response(data_actif)
        processed_passif = replace_and_generate_response(data_passif)
        processed_question = replace_and_generate_response(data_question)
        processed_error = replace_and_generate_error(data_error)

        merged_data = merge_datasets(
            processed_actif, processed_passif, processed_question, processed_error
        )

        write_data_to_csv(merged_data, Dataset)


if __name__ == "__main__":
    dataset = BuildDataset()
    dataset.build()
