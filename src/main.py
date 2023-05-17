import sys
from argparse import ArgumentParser, Namespace
from typing import List, Any
from types import ModuleType
from dotenv import load_dotenv
from models.AbstractLanguageModel import AbstractLanguageModel
from models import *
import models
from testers.ModelTester import ModelTester
from testers.DatasetLoader import DatasetLoader
import testers
from scripts.generate_improvement_files import create_txt_population_foreach_json, create_params_file


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
    return getattr(mod, class_name)()


def main():
    cmd_args: Namespace = set_parser().parse_args()
    load_dotenv()

    if cmd_args.jsons_dir == None:
        if (cmd_args.model not in models.models_list) or (cmd_args.model == None):
            raise Exception(f"Model '{cmd_args.model}' not valid.")
        if (cmd_args.dataset not in testers.datasets_list) or (cmd_args.dataset == None):
            raise Exception(f"Dataset '{cmd_args.dataset}' not valid.")
        model: AbstractLanguageModel = create_instance_of_class("models." + cmd_args.model, cmd_args.model)
        args: List[Any] = [cmd_args.dataset]
        if cmd_args.data_size != None:
            args.append(cmd_args.data_size)
        loader: DatasetLoader = DatasetLoader(*args)
        args.clear()
        args.extend([model, loader])
        if cmd_args.iterations != None:
            args.append(cmd_args.iterations)
        tester: ModelTester = ModelTester(*args)
        results_path: str = tester.run()

    if cmd_args.jsons_dir != None:
        results_path: str = cmd_args.jsons_dir
        print(f"\n{'=' * 80}")
    print("Creation of txt files representing the initial population")
    impr_filenames: List[str] = create_txt_population_foreach_json(results_path)
    print("Creation of txt files containing the parameters of each problem for genetic improvement")
    params_dir_path: str = create_params_file(results_path, impr_filenames)
    print(f"The files have been saved in '{params_dir_path}'")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
