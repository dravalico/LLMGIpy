import os
from os import chdir
from typing import List, Any, Dict, Tuple
from scripts.ponyge.txt_individuals_from_json import txt_population
import ast
from scripts.imports_and_prompt import extract_prompt_info_with_keybert, extract_numbers_from_string
from scripts.function_util import orderering_preserving_duplicates_elimination
from scripts.json_data_io import read_json, create_dir_path_string
import sys
curr_path = [sss for sss in sys.path]
sys.path.append('../PonyGE2/src')
from utilities.stats.file_io import create_results_folder_path # type: ignore
sys.path = curr_path
from models.GrammarGeneratorLLM import GrammarGeneratorLLM

# def create_txt_population_foreach_json(jsons_dir_path: str, task_llm_grammar_generator: str | None = None) -> Any:
def create_txt_population_foreach_json(jsons_dir_path: str, llm_param: dict[str, Any], only_impr: bool, task_llm_grammar_generator = None) -> Any:
    impr_prob_names: List[Tuple[int, str]] = []
    grammars_filenames: List[str] = []
    if task_llm_grammar_generator is not None:
        grammarGenerator = GrammarGeneratorLLM(grammar_task = task_llm_grammar_generator)
    else:
        grammarGenerator = None
    
    model_name: str = llm_param['model_name']
    benchmark_name: str = llm_param['benchmark_name']
    start_problem: int = int(llm_param['start_problem'])
    end_problem: int = int(llm_param['end_problem'])
    iterations: int = int(llm_param['iterations'])
    train_size: int = int(llm_param['train_size'])
    test_size: int = int(llm_param['test_size'])

    for problem_index in range(start_problem, end_problem + 1):
        bnf_filename, problem_name = create_grammar_from(
            json_path=jsons_dir_path,
            problem_index=problem_index,
            model_name=model_name,
            benchmark_name=benchmark_name,
            iterations=iterations,
            train_size=train_size,
            test_size=test_size,
            only_impr=only_impr,
            grammarGenerator=grammarGenerator
        )
        
        try:
            txt_population(
                json_path=jsons_dir_path,
                model_name=model_name,
                benchmark_name=benchmark_name,
                problem_index=problem_index,
                iterations=iterations,
                train_size=train_size,
                test_size=test_size,
                only_impr=only_impr,
                grammar_file=bnf_filename[bnf_filename.rindex('dynamic'):],
                output_dir_name=bnf_filename[bnf_filename.rindex('dynamic') + len('dynamic') + 1:bnf_filename.rindex('.bnf')] + '/'
            )
            print(f"'problem {problem_index}' leads to a valid seed for improvement")
            impr_prob_names.append((problem_index, problem_name))
            grammars_filenames.append(bnf_filename[bnf_filename.rindex('dynamic') + len('dynamic') + 1:])
        except Exception as e:
            print(e)
            print(f"'problem {problem_index}' raises an exception; no population generated")
    if len(impr_prob_names) == 0:
        e: str = "\nNone of given jsons lead to a valid seed for improvement"
        raise Exception(e)
    return impr_prob_names, grammars_filenames


# def create_grammar_from(json_path: str, task_llm_grammar_generator: str | None) -> str:
def create_grammar_from(
        json_path,
        problem_index,
        model_name,
        benchmark_name,
        iterations,
        train_size,
        test_size,
        only_impr,
        grammarGenerator
    ) -> Tuple[str, str]:
    cwd: str = os.getcwd()
    chdir("../PonyGE2/grammars")
    if not os.path.isdir("dynamic"):
        os.mkdir("dynamic")
    chdir("dynamic")
    
    json_file: dict[str, Any] = read_json(
        full_path=json_path,
        model_name=model_name,
        problem_benchmark=benchmark_name,
        problem_id=problem_index,
        reask=False,
        iterations=iterations,
        repeatitions=0,
        train_size=train_size,
        test_size=test_size
    )

    data: List[Dict[str, Any]] = json_file["data_preprocess"]
    n_inputs: int = int(json_file["n_inputs"])
    problem_name: str = json_file["problem_name"]
    extracted_functions_from_individuals: List[List[str]] = []
    extracted_strings_from_individuals: List[List[str]] = []
    variables: List[List[str]] = []
    imports: List[List[str]] = []
    nums = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
    
    for e in data:
        if "main_func" not in e:
            e["main_func"] = '\n'.join([f'def evolve({", ".join(f"v{i}" for i in range(n_inputs))}):', '\tpass'])
        if "variables_names" not in e:
            e["variables_names"] = []
        if "imports" not in e:
            e["imports"] = []
        
        if not only_impr:
            extracted_functions_from_individuals.append(extract_functions_and_methods(e["main_func"]))
            res_strings = extract_strings(e["main_func"])
            prompt_info_strings = extract_prompt_info_with_keybert(json_file["problem_description"])
            extracted_strings_from_individuals.append(res_strings + prompt_info_strings)
            nums.append(extract_numbers_from_string(json_file["problem_description"]))
            variables.append(e["variables_names"])
            imports.append(e["imports"])
    
    temp0: str = ""
    temp: str = ""
    flat_list = [item for sublist in extracted_functions_from_individuals for item in sublist]
    for i in flat_list:
        if "." in i and i not in temp0:
            temp0 += f'"{i}" | '
        elif "." not in i and i not in temp:
            temp += f'"{i}" | '
    temp0 = temp0[:-2]
    temp = temp[:-2]
    temp1: str = []
    flat_list1 = [item for sublist in extracted_strings_from_individuals for item in sublist]
    for i in flat_list1:
        if f'"\'{i}\'"' not in temp1:
            temp1.append(f'"\'{i}\'"')
            temp1.append(" | ")
    temp1 = temp1[:-1]
    temp2: str = ""
    flat_list2 = [item for sublist in variables for item in sublist]
    for i in flat_list2:
        if i not in temp2:
            temp2 += f'"{i}" | '
    temp2 = temp2[:-2]
    temp2 += '| "a0" | "a1" | "a2"'
    temp3: str = ""
    flat_list3 = [item for sublist in imports for item in sublist]
    for i in flat_list3:
        if i not in temp3:
            temp3 += i + '#'
    temp4: str = ""
    flat_list4 = [item for sublist in nums for item in sublist]
    for i in flat_list4:
        if str(i) not in temp4:
            temp4 += f'"{i}" | '
    temp4 = temp4[:-2]

    actual_grammar_path: str = create_dir_path_string(
        full_path=os.getcwd() + '/',
        model_name=model_name,
        problem_benchmark=benchmark_name,
        problem_id=problem_index,
        reask=False,
        iterations=iterations,
        repeatitions=0,
        train_size=train_size,
        test_size=test_size
    )
    last_slash_index: int = actual_grammar_path.rindex('/')
    prefix_actual_grammar_path: str = actual_grammar_path[:last_slash_index + 1]
    if not os.path.isdir(prefix_actual_grammar_path):
        os.makedirs(prefix_actual_grammar_path)
    
    if not only_impr:
        with open("dynamic.bnf", 'rb') as source_file, open(actual_grammar_path.replace(".json", ".bnf"), 'wb') as dest_file:
            dest_file.write(source_file.read())
        
        with open(actual_grammar_path.replace(".json", ".bnf"), 'a') as bnf:
            if temp != "":
                bnf.write("<FUNC> ::= " + temp + '\n')
            else:
                bnf.write("<FUNC> ::= " + '""' + '\n')
            if temp0 != "":
                bnf.write("<METHOD> ::= " + temp0 + '\n')
            else:
                bnf.write("<METHOD> ::= " + '""' + '\n')
            if temp1 != []:
                bnf.write("<STRINGS> ::= " + ''.join(temp1) + '\n')
            else:
                bnf.write("<STRINGS> ::= " + '""' + '\n')
            if temp2 != "":
                bnf.write("<var> ::= " + temp2 + '\n')
            else:
                bnf.write("<var> ::= " + '""' + '\n')
            bnf.write("<num> ::= " + temp4 + '\n')
            bnf.write('<IMPORTS> ::= "' + temp3 + '"' + ' | ' + '""' + '\n')
    
        if grammarGenerator is not None:
            for i, e in enumerate(data): # where data = json_file["data_preprocess"]
               generated_bnfs = grammarGenerator.ask_just_grammar(prompt=json_file["problem_description"], code=e["main_func"], grammar_path=actual_grammar_path.replace(".json", ".bnf"))
               with open(json_path.split('/')[-1].replace(".json", f"_generated_iteration{i}.bnf"), 'w') as bnf_generated: # ! add a folder where put the files
                    bnf_generated.write(generated_bnfs)
    
    chdir(cwd)
    return actual_grammar_path.replace(".json", ".bnf"), problem_name


def extract_functions_and_methods(code: str) -> List[str]:
    function_and_method_names = []
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                function_and_method_names.append(func_name)
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    # obj_name = node.func.value.id
                    method_name = node.func.attr
                    function_and_method_names.append(f".{method_name}")
                elif isinstance(node.func.value, ast.Subscript):
                    if isinstance(node.func.value.value, ast.Name):
                        # obj_name = node.func.value.value.id
                        method_name = node.func.attr
                        function_and_method_names.append(f".{method_name}")
    return function_and_method_names


def extract_strings(code: str) -> List[str]:
    strings = []
    tree = ast.parse(code)

    class StringExtractor(ast.NodeVisitor):
        def visit_Str(self, node):
            strings.append(node.s)
    string_extractor = StringExtractor()
    string_extractor.visit(tree)
    return orderering_preserving_duplicates_elimination(strings)


# NOTE maybe ponyge related things can be enucleated
MODEL_NAME_TAG: str = "<modelName>"
BENCHMARK_NAME_TAG: str = "<benchmarkName>"
PROBLEM_INDEX_TAG: str = "<problemIndex>"
LLM_ITERATIONS_TAG: str = "<llmIterations>"
BNF_GRAMMAR_TAG: str = "<bnf>"
TRAIN_DATASET_TAG: str = "<train>"
TEST_DATASET_TAG: str = "<test>"
NUM_TRAIN_EXAMPLES_TAG: str = "<numTrainExamples>"
NUM_TEST_EXAMPLES_TAG: str = "<numTestExamples>"
FITNESS_FILE_TAG: str = "<fitnessFile>"
SEED_FOLDER_TAG: str = "<seedFolder>"
POPULATION_SIZE_TAG: str = "<populationSize>"
GENERATIONS_TAG: str = "<generations>"
CROSSOVER_TAG: str = "<crossover>"
CROSSOVER_PROBABILITY_TAG: str = "<crossoverProbability>"
MUTATION_TAG: str = "<mutation>"
MUTATION_PROBABILITY_TAG: str = "<mutationProbability>"
SELECTION_TAG: str = "<selection>"
TOURNAMENT_SIZE_TAG: str = "<tournamentSize>"
RANDOM_SEED_TAG: str = "<randomSeed>"


def create_params_file(
        impr_prob_names: List[Tuple[int, str]],
        grammars_filenames: List[str],
        llm_param: dict[str, Any],
        pony_param: dict[str, Any]
    ) -> List[str]:
    cwd: str = os.getcwd()
    chdir("../PonyGE2/parameters")
    improvement_dir: str = "improvements"
    if not os.path.isdir(improvement_dir):
        os.mkdir(improvement_dir)
    with open(f"{improvement_dir}/progimpr_base.txt", 'r') as file:
        impr_base_file: str = file.read()
    
    all_output_paths: List[str] = []
    all_random_seeds: List[int] = list(range(int(llm_param['iterations'])))
    for random_seed in all_random_seeds:
        for (impr_prob_name, grammar_filename) in zip(impr_prob_names, grammars_filenames):
            prob_index: int = impr_prob_name[0]
            prob_name: int = impr_prob_name[1]
            sel_alg: str = pony_param['selection']
            tourn_size: int = 2
            if sel_alg.startswith('tournament'):
                tourn_size = int(sel_alg[len('tournament'):])
                sel_alg = 'tournament'
            params_dir_path: str = create_results_folder_path(
                base_path=improvement_dir + '/',
                params={
                    'BENCHMARK_NAME': llm_param['benchmark_name'],
                    'MODEL_NAME': llm_param['model_name'],
                    'FITNESS_FUNCTION': 'progimpr',
                    'FITNESS_FILE': pony_param['fitness_file'],
                    'NUM_TRAIN_EXAMPLES': int(llm_param['train_size']),
                    'NUM_TEST_EXAMPLES': int(llm_param['test_size']),
                    'SELECTION': sel_alg,
                    'TOURNAMENT_SIZE': tourn_size,
                    'POPULATION_SIZE': int(pony_param['pop_size']),
                    'GENERATIONS': int(pony_param['num_gen']),
                    'CROSSOVER': pony_param['crossover'],
                    'MUTATION': pony_param['mutation'],
                    'CROSSOVER_PROBABILITY': float(pony_param['crossover_probability']),
                    'MUTATION_PROBABILITY': float(pony_param['mutation_probability']),
                    'PROBLEM_INDEX': prob_index,
                    'RANDOM_SEED': random_seed
                },
                include_seed=True,
                make_dirs=False
            )
            path_no_ext: str = grammar_filename[:grammar_filename.rindex('.bnf')]
            impr_file: str = impr_base_file.replace(SEED_FOLDER_TAG, path_no_ext)
            impr_file = impr_file.replace(BNF_GRAMMAR_TAG, grammar_filename)
            impr_file = impr_file.replace(TRAIN_DATASET_TAG, llm_param['benchmark_name'] + '-bench' + '/' + prob_name)
            impr_file = impr_file.replace(TEST_DATASET_TAG, llm_param['benchmark_name'] + '-bench' + '/' + prob_name)
            
            impr_file = impr_file.replace(MODEL_NAME_TAG, llm_param['model_name'])
            impr_file = impr_file.replace(BENCHMARK_NAME_TAG, llm_param['benchmark_name'])
            impr_file = impr_file.replace(PROBLEM_INDEX_TAG, str(prob_index))
            impr_file = impr_file.replace(LLM_ITERATIONS_TAG, str(llm_param['iterations']))
            impr_file = impr_file.replace(NUM_TRAIN_EXAMPLES_TAG, str(llm_param['train_size']))
            impr_file = impr_file.replace(NUM_TEST_EXAMPLES_TAG, str(llm_param['test_size']))
            impr_file = impr_file.replace(FITNESS_FILE_TAG, pony_param['fitness_file'])
            impr_file = impr_file.replace(POPULATION_SIZE_TAG, str(pony_param['pop_size']))
            impr_file = impr_file.replace(GENERATIONS_TAG, str(pony_param['num_gen']))
            impr_file = impr_file.replace(CROSSOVER_TAG, pony_param['crossover'])
            impr_file = impr_file.replace(CROSSOVER_PROBABILITY_TAG, str(pony_param['crossover_probability']))
            impr_file = impr_file.replace(MUTATION_TAG, pony_param['mutation'])
            impr_file = impr_file.replace(MUTATION_PROBABILITY_TAG, str(pony_param['mutation_probability']))
            impr_file = impr_file.replace(SELECTION_TAG, sel_alg)
            impr_file = impr_file.replace(TOURNAMENT_SIZE_TAG, str(tourn_size))
            impr_file = impr_file.replace(RANDOM_SEED_TAG, str(random_seed))

            if params_dir_path.endswith('/'):
                params_dir_path = params_dir_path[:-1]

            if not os.path.isdir(params_dir_path[:params_dir_path.rindex('/')]):
                os.makedirs(params_dir_path[:params_dir_path.rindex('/')])

            output_filepath: str = os.path.join(params_dir_path[:params_dir_path.rindex('/')], params_dir_path[params_dir_path.rindex('/') + 1:] + '.txt')
            output_file = open(output_filepath, 'w')
            output_file.write(impr_file)
            output_file.close()
            all_output_paths.append(output_filepath)
    
    chdir(cwd)
    return all_output_paths
