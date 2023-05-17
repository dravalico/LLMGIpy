from models.AbstractLanguageModel import AbstractLanguageModel
from models import *
import models
from testers.ModelTester import ModelTester
from testers.DatasetLoader import DatasetLoader
import testers
from scripts.generate_improvement_files import create_txt_population_foreach_json, create_params_file
from argparse import ArgumentParser, Namespace
from typing import List, Any
from types import ModuleType
import sys
from dotenv import load_dotenv


def set_parser() -> ArgumentParser:
    argparser: ArgumentParser = ArgumentParser(description="GI improvement from LLM response")
    argparser.add_argument("--model", type=str, help=f"The LLM's name: {models.models_list}")
    argparser.add_argument("--dataset", type=str, help=f"The dataset to use for tests: {testers.datasets_list}")
    argparser.add_argument("--data_size", type=int, help="Length of the test dataset")
    argparser.add_argument("--iterations",
                           type=int,
                           help="Number of times to repete question and test for the same problem")
    argparser.add_argument("--jsons_dir",
                           type=str,
                           help="Generate only improvement files; needs the path of jsons directory")
    argparser.add_argument("-v", "--verbose", action="store_true", help="Print everything")  # TODO complete it
    return argparser


def create_instance_of_class(module_name: str, class_name: str) -> Any:
    mod: ModuleType = sys.modules[module_name]
    return getattr(mod, class_name)


def main():
    args: Namespace = set_parser().parse_args()
    load_dotenv()

    if args.jsons_dir == None:
        if (args.model not in models.models_list) or (args.model == None):
            raise Exception(f"Model '{args.model}' not valid.")
        if (args.dataset not in testers.datasets_list) or (args.dataset == None):
            raise Exception(f"Dataset '{args.dataset}' not valid.")
        model: AbstractLanguageModel = create_instance_of_class("models." + args.model, args.model)
        loader: DatasetLoader = DatasetLoader(args.dataset, args.data_size) \
            if args.data_size != None else DatasetLoader(args.dataset)
        tester_args: List[Any] = [model, loader]
        if args.iterations != None:
            tester_args.append(args.iterations)
        tester: ModelTester = ModelTester(*tester_args)
        results_path: str = tester.run()

    if args.jsons_dir != None:
        results_path: str = args.jsons_dir
    impr_filenames: List[str] = create_txt_population_foreach_json(results_path)
    params_dir_path: str = create_params_file(results_path, impr_filenames)


if __name__ == "__main__":
    main()
