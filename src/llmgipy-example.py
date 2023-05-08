from models.AbstractLanguageModel import AbstractLanguageModel
from models.AlpacaModel import AlpacaModel
from testers.ModelTester import ModelTester
from testers.DatasetLoader import DatasetLoader


def main():
    model: AbstractLanguageModel = AlpacaModel()
    loader: DatasetLoader = DatasetLoader()
    loader.set_problems_to_psb2()
    tester: ModelTester = ModelTester(
        model,
        loader.problems,
        loader.load_psb2_data,
        iterations=2
    )
    tester.run()


if __name__ == "__main__":
    main()
