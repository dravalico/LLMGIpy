from models.AbstractLanguageModel import AbstractLanguageModel
from models import *
import models
from testers.ModelTester import ModelTester
from testers.DatasetLoader import DatasetLoader
from scripts.txt_individuals_from_json import txt_population
import testers
from argparse import ArgumentParser, Namespace
from typing import List, Any, Dict
import sys
import os
from os import listdir, chdir
from os.path import isfile, join
import json


def set_parser() -> ArgumentParser:
    argparser: ArgumentParser = ArgumentParser(description="GI improvement from LLM response")
    argparser.add_argument("--model", type=str, help=f"The LLM's name: {models.models_list}")
    argparser.add_argument("--dataset", type=str, help=f"The dataset to use for tests: {testers.datasets_list}")
    argparser.add_argument("--data_size", type=int, help="Length of the test dataset")
    argparser.add_argument("--iterations",
                           type=int,
                           help="Number of times to repete question and test for the same problem")
    argparser.add_argument("-v", "--verbose", action="store_true", help="Print everything")  # TODO complete it
    return argparser


def create_instance_of_class(module_name: str, class_name: str) -> Any:
    mod = sys.modules[module_name]
    cls: Any = getattr(mod, class_name)
    inst: Any = cls()
    return inst


def main():
    args: Namespace = set_parser().parse_args()
    if (args.model not in models.models_list) or (args.model == None):
        raise Exception(f"Model '{args.model}' not valid.")
    if (args.dataset not in testers.datasets_list) or (args.dataset == None):
        raise Exception(f"Dataset '{args.dataset}' not valid.")
    """ # TODO remove comment
    model: AbstractLanguageModel = create_instance_of_class("models." + args.model, args.model)

    loader: DatasetLoader = DatasetLoader(args.dataset, args.data_size) \
        if args.data_size != None else DatasetLoader(args.dataset)

    tester_args: List[Any] = [model, loader]
    if args.iterations != None:
        tester_args.append(args.iterations)

    tester: ModelTester = ModelTester(*tester_args)
    jsons_dir_path: str = tester.run()
    """
    tests_results: str = "/mnt/data/dravalico/workspace/LLMGIpy/results/2023-05-10_15:50:00"
    json_filenames: List[str] = [f for f in listdir(tests_results) if isfile(join(tests_results, f))]
    to_impr_filenames: List[str] = []
    jsons_dir_name: str = tests_results.split('/')[-1]
    for filename in json_filenames:
        try:
            txt_population(tests_results + '/' + filename,
                           "progsys/Fizz Buzz.bnf",  # TODO grammar from csv of problems
                           jsons_dir_name + '_' + filename.replace(".json", ''))
            to_impr_filenames.append(filename)
        except Exception as e:
            print(f"{filename} raises an exception: {str(e)}")
    if len(to_impr_filenames) == 0:
        e: str = "None of given jsons lead to a valid seed for improvement"
        raise Exception(e)
    chdir("../PonyGE2/parameters")
    with open("./progimpr_base.txt", 'r') as file:
        impr_base_file: str = file.read()
    base_path: str = "./improvement/"
    if not os.path.isdir(base_path):
        os.mkdir(base_path)
    params_dir_path: str = os.path.join(base_path, jsons_dir_name)
    if not os.path.isdir(params_dir_path):
        os.mkdir(params_dir_path)
    for impr_filename in to_impr_filenames:
        impr_file: str = impr_base_file.replace(
            "<seed_folder>",
            jsons_dir_name + '_' + impr_filename.replace(".json", ''))
        with open(os.path.join(tests_results, impr_filename), "r") as read_file:
            extracted_json: Any = json.load(read_file)
        prob_name: List[Dict[str, Any]] = extracted_json["problem_name"]
        impr_file = impr_file.replace(
            "<train>",
            prob_name)
        impr_file = impr_file.replace(
            "<test>",
            prob_name)
        output_filepath: str = os.path.join(params_dir_path, impr_filename.replace(".json", "txt"))
        output_file = open(output_filepath, 'w')
        output_file.write(impr_file)
        output_file.close()


if __name__ == "__main__":
    main()
