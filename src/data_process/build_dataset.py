from utils import write_data_to_csv, load_sncf_data
import data.example_sentences as es


class BuildDataset:
    """
    A class to load and build a dataset from SNCF data and write it to a CSV file.

    Attributes:
        data (list): The SNCF dataset loaded during initialization.
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
        write_data_to_csv(es.data)


if __name__ == "__main__":
    dataset = BuildDataset()
    dataset.build()
