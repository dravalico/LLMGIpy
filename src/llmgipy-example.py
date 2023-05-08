from models.AbstractLanguageModel import AbstractLanguageModel
from models.AlpacaModel import AlpacaModel
from testers.ModelTester import ModelTester


def main():
    model: AbstractLanguageModel = AlpacaModel()
    model_tester: ModelTester = ModelTester(model, "psb2", iterations=2)
    model_tester.run()


if __name__ == "__main__":
    main()
