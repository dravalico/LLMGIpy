import AlpacaModel
import PSB2ModelTester


def main():
    alpaca_model: AlpacaModel.AlpacaModel = AlpacaModel.AlpacaModel()
    model_tester: PSB2ModelTester.PSB2ModelTester = PSB2ModelTester.PSB2ModelTester(
        1, 2000, alpaca_model
    )
    model_tester.run()


if __name__ == "__main__":
    main()
