from AbstractLanguageModel import AbstractLanguageModel
from AlpacaModel import AlpacaModel
from AbstractModelTester import AbstractModelTester
from PSB2ModelTester import PSB2ModelTester
from scripts.JSON_data_saver import create_json_file


def main():
    alpaca_model: AbstractLanguageModel = AlpacaModel()
    model_tester: AbstractModelTester = PSB2ModelTester(
        alpaca_model, test_iteration=2)
    model_tester.run()


if __name__ == "__main__":
    main()
