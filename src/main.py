import AbstractLanguageModel
import AlpacaModel
import AbstractModelTester
import PSB2ModelTester


def main():
    alpaca_model: AbstractLanguageModel.AbstractLanguageModel = AlpacaModel.AlpacaModel()
    model_tester: AbstractModelTester.AbstractModelTester = PSB2ModelTester.PSB2ModelTester(
        1, 2000, alpaca_model
    )
    model_tester.run()


if __name__ == "__main__":
    main()
