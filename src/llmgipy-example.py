from models.AbstractLanguageModel import AbstractLanguageModel
from models.AlpacaModel import AlpacaModel
from testers.ModelTester import ModelTester
from testers.test import TesterTest


def main():
    model: AbstractLanguageModel = AlpacaModel()
    model_tester: TesterTest = TesterTest(model, "psb2", iterations=2)
    model_tester.run()


if __name__ == "__main__":
    main()
