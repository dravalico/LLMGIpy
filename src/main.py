import sys
from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from typing import List, Any
from types import ModuleType
from dotenv import load_dotenv
from models.AbstractLanguageModel import AbstractLanguageModel
from models import *
import models
from testers.ModelTester import ModelTester
from testers.DatasetLoader import DatasetLoader
import testers
from scripts.ponyge.improvement_files_generator import create_txt_population_foreach_json, create_params_file


def set_parser() -> ArgumentParser:
    argparser: ArgumentParser = ArgumentParser(description="GI improvement from LLM response")
    argparser.add_argument("--model", type=str, help=f"The LLM's name: {models.models_list}")
    argparser.add_argument("--dataset", type=str, help=f"The dataset to use for tests: {testers.datasets_list}")
    argparser.add_argument("--train_size", type=int, help="Length of the test dataset")
    argparser.add_argument("--iterations",
                           type=int,
                           help="Number of times to repete question and test for the same problem")
    argparser.add_argument("--impr_files",
                           action=BooleanOptionalAction,
                           help="Boolean flag to generate also the files necessary for the improvement part")
    argparser.add_argument("--jsons_dir",
                           type=str,
                           help="Generate only improvement files; needs the path of jsons directory")
    argparser.add_argument("--reask",
                           action=BooleanOptionalAction,
                           help="Boolean flag to ask the model to correct the answer if wrong")
    return argparser


def create_instance_of_class(module_name: str, class_name: str, **kwargs) -> Any:
    mod: ModuleType = sys.modules[module_name]
    return getattr(mod, class_name)(**kwargs)


def main():
    cmd_args: Namespace = set_parser().parse_args()
    load_dotenv()

    if cmd_args.jsons_dir is None:
        if (cmd_args.model not in models.models_list) or (cmd_args.model is None):
            raise Exception(f"Model '{cmd_args.model}' not valid.")
        if (cmd_args.dataset not in testers.datasets_list) or (cmd_args.dataset is None):
            raise Exception(f"Dataset '{cmd_args.dataset}' not valid.")
        if cmd_args.train_size is None:
            raise Exception(f"Train Size '{cmd_args.train_size}' must be inserted.")
        if cmd_args.train_size is not None and cmd_args.train_size > 1000:
            raise Exception(f"Train Size '{cmd_args.train_size}' is greater than 1000, It is too large!")
        model: AbstractLanguageModel = create_instance_of_class("models." + cmd_args.model, cmd_args.model, problem_bench=cmd_args.dataset)
        args: List[Any] = [cmd_args.dataset]
        args.append(cmd_args.train_size)
        loader: DatasetLoader = DatasetLoader(*args)
        args.clear()
        args.extend([model, loader])
        if cmd_args.iterations != None:
            args.append(cmd_args.iterations)
        if cmd_args.reask:
            args.append("reask = True")
        tester: ModelTester = ModelTester(*args)
        if cmd_args.reask:
            tester.run_with_reask()
            return
        else:
            results_path: str = tester.run()

    if cmd_args.jsons_dir != None:
        results_path: str = cmd_args.jsons_dir
        print(f"\n{'=' * 80}")

    if cmd_args.impr_files or cmd_args.jsons_dir != None:
        print("Creation of txt files representing the initial population")
        try:
            impr_filenames, grammars_filenames = create_txt_population_foreach_json(results_path)
            print("Creation of txt files containing the parameters of each problem for genetic improvement")
            params_dir_path: str = create_params_file(results_path, impr_filenames, grammars_filenames)
            print(f"The files have been saved in '{params_dir_path}'")
        except Exception as e:
            print(e)
        finally:
            print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
