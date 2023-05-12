from models.AbstractLanguageModel import AbstractLanguageModel
from models.AlpacaModel import AlpacaModel
from testers.ModelTester import ModelTester
from testers.DatasetLoader import DatasetLoader
from argparse import ArgumentParser, Namespace
from typing import List, Any
import sys

_MODELS: List[str] = ["Alpaca"]
_DATASETS: List[str] = ["psb2"]


def create_object(modulename, classname):
    mod = sys.modules[modulename]
    cls = getattr(mod, classname)
    inst = cls()
    return inst


def main():
    argparser: ArgumentParser = ArgumentParser(description="GI improvement from LLM response")
    argparser.add_argument("--model", type=str, help="The LLM's name: " + str(_MODELS))
    argparser.add_argument("--dataset", type=str, help="The dataset to use for tests: " + str(_DATASETS))
    argparser.add_argument("--data_size", type=int, help="Length of the test dataset")
    argparser.add_argument("--iterations", type=int,
                           help="Number of times to repete question and test for the same problem")
    args: Namespace = argparser.parse_args()
    if (args.model not in _MODELS) or (args.model == None):
        raise Exception("Model not valid.")
    if (args.dataset not in _DATASETS) or (args.dataset == None):
        raise Exception("Dataset not valid.")

    # model: AbstractLanguageModel = create_object(args.model + "Model", args.model + "Model")
    model: AbstractLanguageModel = AlpacaModel()

    loader: DatasetLoader = DatasetLoader(args.dataset, args.data_size) \
        if args.data_size != None else DatasetLoader(args.dataset)

    tester_args: List[Any] = [model, loader]
    if args.iterations != None:
        tester_args.append(args.iterations)

    tester: ModelTester = ModelTester(*tester_args)
    result_dir_path: str = tester.run()


if __name__ == "__main__":
    main()
