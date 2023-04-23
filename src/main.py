from src.models.AbstractLanguageModel import AbstractLanguageModel
from src.models.AlpacaModel import AlpacaModel
from src.testers.AbstractModelTester import AbstractModelTester
from src.testers.PSB2ModelTester import PSB2ModelTester


def main():
    alpaca_model: AbstractLanguageModel = AlpacaModel()
    model_tester: AbstractModelTester = PSB2ModelTester(alpaca_model)
    model_tester.run()


if __name__ == "__main__":
    main()
