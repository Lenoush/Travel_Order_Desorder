from utils import write_data_to_csv, load_sncf_data
import data.example_sentences as es


class BuildDataset:
    def __init__(self):
        self.data = load_sncf_data()

    def build(self):
        write_data_to_csv(es.data)


if __name__ == "__main__":
    dataset = BuildDataset()
    dataset.build()
