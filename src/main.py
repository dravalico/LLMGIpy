from models.AbstractLanguageModel import AbstractLanguageModel
from models.AlpacaModel import AlpacaModel
from testers.AbstractModelTester import AbstractModelTester
from testers.PSB2ModelTester import PSB2ModelTester


def main():
    alpaca_model: AbstractLanguageModel = AlpacaModel()
    model_tester: AbstractModelTester = PSB2ModelTester(alpaca_model)
    model_tester.run()


if __name__ == "__main__":
    main()
