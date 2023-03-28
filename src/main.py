from AbstractLanguageModel import AbstractLanguageModel
from AlpacaModel import AlpacaModel
from AbstractModelTester import AbstractModelTester
from PSB2ModelTester import PSB2ModelTester


def main():
    alpaca_model: AbstractLanguageModel = AlpacaModel()
    model_tester: AbstractModelTester = PSB2ModelTester(1, 2000, alpaca_model)
    model_tester.run()


if __name__ == "__main__":
    main()
