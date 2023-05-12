from models.AbstractLanguageModel import AbstractLanguageModel
from models import *
import models
from testers.ModelTester import ModelTester
from testers.DatasetLoader import DatasetLoader
import testers
from argparse import ArgumentParser, Namespace
from typing import List, Any
import sys
from os import listdir, chdir
from os.path import isfile, join


def create_object(module_name: str, class_name: str) -> Any:
    mod = sys.modules[module_name]
    cls: Any = getattr(mod, class_name)
    inst: Any = cls()
    return inst


def main():
    argparser: ArgumentParser = ArgumentParser(description="GI improvement from LLM response")
    argparser.add_argument("--model", type=str, help=f"The LLM's name: {models.models_list}")
    argparser.add_argument("--dataset", type=str, help=f"The dataset to use for tests: {testers.datasets_list}")
    argparser.add_argument("--data_size", type=int, help="Length of the test dataset")
    argparser.add_argument("--iterations", type=int,
                           help="Number of times to repete question and test for the same problem")
    argparser.add_argument("-v", "--verbose", action="store_true", help="Print everything") # TODO complete it
    args: Namespace = argparser.parse_args()
    if (args.model not in models.models_list) or (args.model == None):
        raise Exception(f"Model '{args.model}' not valid.")
    if (args.dataset not in testers.datasets_list) or (args.dataset == None):
        raise Exception(f"Dataset '{args.dataset}' not valid.")
    """ # TODO remove comment
    model: AbstractLanguageModel = create_object("models." + args.model, args.model)

    loader: DatasetLoader = DatasetLoader(args.dataset, args.data_size) \
        if args.data_size != None else DatasetLoader(args.dataset)

    tester_args: List[Any] = [model, loader]
    if args.iterations != None:
        tester_args.append(args.iterations)

    tester: ModelTester = ModelTester(*tester_args)
    result_dir_path: str = tester.run()
    """
    result_dir_path: str = "/mnt/data/dravalico/workspace/LLMGIpy/results/2023-05-10_15:50:00"
    jsons = [f for f in listdir(result_dir_path) if isfile(join(result_dir_path, f))]
    sys.path.append('../PonyGE2/src/scripts')
    from txt_individuals_from_json import txt_population
    chdir("../PonyGE2/src")
    for json in jsons:
        ind_dir_name: str = result_dir_path.split("/")[-1] + "_" + json.replace(".json", "")
        txt_population(result_dir_path + "/" + json, "progsys/Fizz Buzz.bnf", ind_dir_name) # TODO grammar from csv of problems


if __name__ == "__main__":
    main()
