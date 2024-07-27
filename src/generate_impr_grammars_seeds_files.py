from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from argparse import RawTextHelpFormatter
from dotenv import load_dotenv
import json
import itertools
from scripts.ponyge.improvement_files_generator import create_txt_population_foreach_json, create_params_file
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

def set_parser_impr() -> ArgumentParser:
    argparser: ArgumentParser = ArgumentParser(
        description="LLM response parser for generating improvement parameters files, grammars files, and seeds files with the initial populations.",
        formatter_class=RawTextHelpFormatter
    )
    argparser.add_argument(
        "--json_params",
        type=str,
        help="Path to the json file containing the parameters to use for generating the improvement files and everything else.\
            \nHow this json file should be formatted?\
            \nThe json file contains two keys: llm_params and pony_params. Each of them has a dictionary as value.\
            \nRegarding llm_params dictionary, it has 5 keys: model_names, benchmark_names, iterations, train_sizes, test_sizes. Each of them has a list as value. Specifically:\
            \n- model_names has a list of strings with all the names of the models\
            \n- benchmark_names has a list of 3-sized lists where the first element is the name of the benchmark, the second element is the start problem index, the third element is the end problem index\
            \n- iterations has a list of integers where each integer depicts the number of iterations\
            \n- train_sizes has a list of integers where each integer depicts the number of test cases in the training set\
            \n- test_sizes has a list of integers where each integer depicts the number of test cases in the test set\
            \nAll possible combinations of these parameters will be considered for generating the evoluton files.\
            \nRegarding pony_params dictionary, it has 7 keys: fitness_files, selections, pop_gens, crossovers, crossover_probabilities, mutations, mutation_probabilities. Each of them has a list as value. Specifically:\
            \n- fitness_files has a list of strings with all the names of the fitness files (including the extension)\
            \n- selections has a list of strings with all the selection algorithms to use (in case of tournament, the tournament size is appendend at the end of the string)\
            \n- pop_gens has a list of 2-sized lists where the first element is the population size and the second element is the number of generations\
            \n- crossovers has a list of strings with all the crossover algorithms to use\
            \n- crossover_probabilities has a list of float with all the crossover probabilities\
            \n- mutations has a list of strings with all the mutation algorithms to use\
            \n- mutation_probabilities has a list of float with all the mutation probabilities\
            \nAll possible combinations of these parameters will be considered for generating the evoluton files.\
            \nEach of those combinations will be paired with all the possible combinations of the parameters in llm_params dictionary.\n"
    )
    argparser.add_argument(
        "--results_dir",
        type=str,
        help="Path of the directory containing the complete directory hierarchy with the results of the LLM without reask. Must end with /."
    )
    argparser.add_argument(
        "--only_impr",
        action=BooleanOptionalAction,
        help="Boolean flag to force the generation of the improvements file only. It requires that seeds and grammars have already been generated before."
    )
    argparser.add_argument(
        "--input_params_ponyge",
        type=str,
        help="Path detailing an empty .txt file with the paths of the improvement parameters files for parallel execution of the evolutionary runs."
    )
    return argparser


def generate_impr_files():
    cmd_args: Namespace = set_parser_impr().parse_args()
    load_dotenv()
    
    print(f"\n{'=' * 80}")

    if cmd_args.json_params is None:
        raise AttributeError("json_params required.")
    
    if cmd_args.results_dir is None:
        raise AttributeError("results_dir required.")
    
    only_impr: bool = cmd_args.only_impr if cmd_args.only_impr else False
    impr_params_path: str = cmd_args.json_params
    results_path: str = cmd_args.results_dir
    if not results_path.endswith('/'):
        results_path += '/'

    with open(impr_params_path, 'r') as f:
        json_params: dict[str, dict[str, list[any]]] = json.load(f)
    
    llm_params = all_llm_params(json_params)
    pony_params = all_pony_params(json_params)
    all_impr_paths = []
    try:
        task_llm_grammar_generator = None
        for llm_param in llm_params:
            print("Creation of txt files representing the initial population")
            print(llm_param)
            print()
            impr_prob_names, grammars_filenames = create_txt_population_foreach_json(
                jsons_dir_path=results_path,
                llm_param=llm_param,
                only_impr=only_impr,
                task_llm_grammar_generator=task_llm_grammar_generator
            )
            if len(impr_prob_names) == 0:
                continue
            for pony_param in pony_params:
                print("Creation of txt files containing the parameters of each problem for genetic improvement")
                print(pony_param)
                print()
                all_impr_paths.extend(create_params_file(
                    impr_prob_names=impr_prob_names,
                    grammars_filenames=grammars_filenames,
                    llm_param=llm_param,
                    pony_param=pony_param
                ))
                print(f"The files have been saved.")
    except Exception as e:
        print(e)
    
    if cmd_args.input_params_ponyge is not None:
        output_file = open(cmd_args.input_params_ponyge, 'w')
        output_file.writelines([lol + '\n' for lol in all_impr_paths])
        output_file.close()

    print(f"{'=' * 80}")


def all_llm_params(json_params):
    llm_params = json_params['llm_params']
    l = [llm_params['model_names'], llm_params['benchmark_names'], llm_params['iterations'], llm_params['train_sizes'], llm_params['test_sizes']]
    l = [el for el in itertools.product(*l)]
    l = [{'model_name': el[0], 'benchmark_name': el[1][0], 'start_problem': el[1][1], 'end_problem': el[1][2], 'iterations': el[2], 'train_size': el[3], 'test_size': el[4]} for el in l]
    return l


def all_pony_params(json_params):
    pony_params = json_params['pony_params']
    l = [pony_params['fitness_files'], pony_params['selections'], pony_params['pop_gens'], pony_params['crossovers'], pony_params['crossover_probabilities'], pony_params['mutations'], pony_params['mutation_probabilities']]
    l = [el for el in itertools.product(*l)]
    l = [{'fitness_file': el[0], 'selection': el[1][0], 'selection_sample_size': el[1][1], 'pop_size': el[2][0], 'num_gen': el[2][1], 'crossover': el[3], 'crossover_probability': el[4], 'mutation': el[5], 'mutation_probability': el[6]} for el in l]
    return l


if __name__ == "__main__":
    generate_impr_files()
