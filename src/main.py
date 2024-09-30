from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from typing import List, Any, Optional
from dotenv import load_dotenv
from models.AbstractLanguageModel import AbstractLanguageModel
import models
from testers.ModelTester import ModelTester
from testers.DatasetLoader import DatasetLoader
import testers
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

for llm_macro_category in models.all_llms_macro_categories:
    exec(f'from models.{llm_macro_category} import {llm_macro_category}')

def set_parser() -> ArgumentParser:
    argparser: ArgumentParser = ArgumentParser(description="LLM response extraction and processing")
    argparser.add_argument("--model", type=str, help=f"The LLM's name: {models.models_list}")
    argparser.add_argument("--dataset", type=str, help=f"The dataset to use for tests: {testers.datasets_list}")
    argparser.add_argument("--prompt_type", type=str, help=f"The type of prompt.")
    argparser.add_argument("--train_size", type=int, help="Length of the test dataset")
    argparser.add_argument("--iterations",
                           type=int,
                           help="Number of times to repeat question and test for the same problem.")
    argparser.add_argument("--repeatitions",
                           type=int,
                           help="Number of repeatitions in the reask method. Ignored if reask is False.")
    argparser.add_argument("--reask",
                           action=BooleanOptionalAction,
                           help="Boolean flag to ask the model to correct the answer if wrong.")
    argparser.add_argument("--problems_indexes",
                           type=str,
                           default='',
                           help="Put the indexes of the problems to execute separated by comma, if it is not provided then all problems are executed.")
    argparser.add_argument("--llm_grammar_generator",
                           type=str,
                           default='',
                           help="Select the methods on how a LLM have to generate the BNF grammar. It can be 'generate_grammar' or 'generate_grammar_from_zero' or 'find_tags_grammar'. ")
    argparser.add_argument("--target_train_size",
                           type=int,
                           default=-1,
                           help="The target train size if LLM output for given train size is already available.")
    
    return argparser


def create_instance_of_class(model_name: str, problem_bench: str, prompt_type: str, load_model: bool, **kwargs) -> Any:
    category_llm = models.ALL_LLMs[model_name][0]
    return eval(category_llm)(model_name=model_name, problem_bench=problem_bench, prompt_type=prompt_type, load_model=load_model, **kwargs)


def main():
    cmd_args: Namespace = set_parser().parse_args()
    load_dotenv()

    if (cmd_args.model not in models.models_list) or (cmd_args.model is None):
        raise Exception(f"Model '{cmd_args.model}' not valid.")
    if (cmd_args.dataset not in testers.datasets_list) or (cmd_args.dataset is None):
        raise Exception(f"Dataset '{cmd_args.dataset}' not valid.")
    if cmd_args.prompt_type is None:
        raise Exception(f"Prompt type must be inserted.")
    if cmd_args.train_size is None:
        raise Exception(f"Train Size '{cmd_args.train_size}' must be inserted.")
    if cmd_args.train_size is not None and cmd_args.train_size > 1000:
        raise Exception(f"Train Size '{cmd_args.train_size}' is greater than 1000, It is too large!")

    if cmd_args.target_train_size is not None and cmd_args.target_train_size > 0:
        if cmd_args.reask:
            raise AttributeError(f'If target train size is specified, then reask must be False.')
        model: AbstractLanguageModel = create_instance_of_class(
            model_name=cmd_args.model,
            problem_bench=cmd_args.dataset,
            prompt_type=cmd_args.prompt_type,
            load_model=False
        )
        loader: DatasetLoader = DatasetLoader(
            dataset=cmd_args.dataset,
            prompt_type=cmd_args.prompt_type,
            train_size=cmd_args.target_train_size,
            test_size=1000
        )
    else:
        model: AbstractLanguageModel = create_instance_of_class(
            model_name=cmd_args.model,
            problem_bench=cmd_args.dataset,
            prompt_type=cmd_args.prompt_type,
            load_model=True
        )

        loader: DatasetLoader = DatasetLoader(
            dataset=cmd_args.dataset,
            prompt_type=cmd_args.prompt_type,
            train_size=cmd_args.train_size,
            test_size=1000
        )

    tester: ModelTester = ModelTester(
        model=model,
        dataset_loader=loader,
        iterations=cmd_args.iterations if cmd_args.iterations is not None else 5,
        reask=cmd_args.reask if cmd_args.reask else False,
        repeatitions=cmd_args.repeatitions if cmd_args.reask else 10,
        train_size=cmd_args.train_size,
        target_train_size=cmd_args.target_train_size
    )

    problems_indexes: Optional[List[int]] = None
    if cmd_args.problems_indexes.strip() != '':
        if '..' in cmd_args.problems_indexes.strip():
            problems_range_to_run = cmd_args.problems_indexes.strip().split('..')
            if len(problems_range_to_run) != 2:
                raise AttributeError(f'If you specify a range of problem indexes, ensure they are just two, found {cmd_args.problems_indexes.strip()}.')
            if int(problems_range_to_run[0]) > int(problems_range_to_run[1]):
                raise AttributeError(f'Invalid problems range, start must be less than or equal than end. Found {int(problems_range_to_run[0])} and {int(problems_range_to_run[1])}.')
            problems_indexes = [int(i) for i in range(int(problems_range_to_run[0]), int(problems_range_to_run[1]) + 1)]
        else:
            problems_indexes = [int(i) for i in cmd_args.problems_indexes.strip().split(',')]
    
    if cmd_args.target_train_size is not None and cmd_args.target_train_size > 0:
        results_path: str = tester.cached_run(problems_indexes=problems_indexes)
        return

    if cmd_args.reask:
        tester.run_with_reask(problems_indexes=problems_indexes)
        return
    else:
        results_path: str = tester.run(problems_indexes=problems_indexes)
        return


if __name__ == "__main__":
    main()
