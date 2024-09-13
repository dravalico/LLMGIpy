import os
import subprocess
import re
import datetime
import uuid
import json
from typing import Any, List, Dict, Tuple
import multiprocessing
from scripts.function_util import orderering_preserving_duplicates_elimination, compute_bnf_type_from_dynamic_bnf_param, DYNAMICBNF_AS_STRING, STATICBNF_AS_STRING
from scripts.json_data_io import read_json, create_dir_path_string, ALREADY_SOLVED_STRING, NOT_PARSED_STRING


def load_phenotypes_from_json(
        json_path: str,
        model_name: str,
        benchmark_name: str,
        benchmark_type: str,
        problem_index: int,
        iterations: int,
        train_size: int,
        test_size: int
    ) -> Tuple[List[str], bool, int, int]:
    json_file: dict[str, Any] = read_json(
        full_path=json_path,
        model_name=model_name,
        problem_benchmark=benchmark_name,
        problem_benchmark_type=benchmark_type,
        problem_id=problem_index,
        reask=False,
        iterations=iterations,
        repeatitions=0,
        train_size=train_size,
        test_size=test_size
    )

    kwarg_variable_name_regex: str = "[a-zA-Z_][a-zA-Z0-9_]*="
    data: List[Dict[str, Any]] = json_file["data_preprocess"]
    n_inputs: int = int(json_file["n_inputs"])

    phenotypes: List[str] = []
    data_train_size: int = int(json_file["data_train_size"])
    
    if data_train_size != train_size:
        raise ValueError(f'Declared train_size {train_size} is different from the data_train_size {data_train_size} found in the results.')
    
    already_solved: bool = False
    num_iter_solved: int = 0
    for i in range(0, len(data)):
        if 'final_individual' in data[i]:
            final_ind: str = data[i]['final_individual'].replace('\u2019', "\'")
            final_ind = final_ind[final_ind.index('def evolve('):].replace('repeat=', '')
            final_ind = final_ind.replace(f' ({data[i]["function_name"]}(', ' (evolve(').replace(f' {data[i]["function_name"]}(', ' evolve(')
            final_ind = final_ind.replace('\\\\b', '\b')
            final_ind = final_ind.replace('\\\\d', '\d')
            final_ind = final_ind.replace('\\\\w', '\w')
            final_ind = final_ind.replace('\\\\s', '\s')
            final_ind = final_ind.replace('\\\\B', '\B')
            final_ind = final_ind.replace('\\\\D', '\D')
            final_ind = final_ind.replace('\\\\W', '\W')
            final_ind = final_ind.replace('\\\\S', '\S')
            final_ind = final_ind.replace('\\b', '\b')
            final_ind = final_ind.replace('\\d', '\d')
            final_ind = final_ind.replace('\\w', '\w')
            final_ind = final_ind.replace('\\s', '\s')
            final_ind = final_ind.replace('\\B', '\B')
            final_ind = final_ind.replace('\\D', '\D')
            final_ind = final_ind.replace('\\W', '\W')
            final_ind = final_ind.replace('\\S', '\S')
            for slash_digit in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                final_ind = final_ind.replace(f'\\\\{slash_digit}', f'\{slash_digit}')
                final_ind = final_ind.replace(f'\\{slash_digit}', f'\{slash_digit}')
        else:
            final_ind: str = ''.join([f'def evolve({", ".join(f"v{i}" for i in range(n_inputs))}):', '{:#pass#:}'])
        if 'tests_results' in data[i] and 'passed' in data[i]["tests_results"] and int(data[i]["tests_results"]["passed"]) == train_size:
            num_iter_solved += 1
        else:
            phenotypes.append(final_ind.replace('!', '\!'))
    if num_iter_solved > 0:
        already_solved = True
    return phenotypes, already_solved, num_iter_solved, len(data)


def parse_genotypes(phenotypes: List[str], grammar_file: str, already_solved: bool, only_impr: bool, dynamic_bnf: str) -> List[List[str]]:
    bnf_type = compute_bnf_type_from_dynamic_bnf_param(dynamic_bnf)
    if only_impr or already_solved: # ! if already solve the dynamic grammar is not generated
        return []
    if len(phenotypes) == 0:
        e: str = "You must specify at least one individual phenotype."
        raise Exception(e)
    
    # REMEMBER TO REPLICATE THE FOLLOWING CODE ALSO IN THE METHOD load_population OF initialisation.py IN PonyGE2
    # Sei in PonyGE2/src
    
    genotypes: List[Any] = [] 
    
    if bnf_type == DYNAMICBNF_AS_STRING:
        args_for_dynamic_bnf: List[Any] = ["--grammar_file", grammar_file, "--reverse_mapping_target", phenotypes[0], "--all_phenotypes", str(phenotypes)]
        worker_function("scripts/GE_LR_parser.py", args_for_dynamic_bnf)
        if os.path.exists(os.path.join('../grammars', grammar_file.replace('.bnf', '_complete_dynamic.bnf'))):
            args: List[Tuple[Any]] = [("scripts/GE_LR_parser.py", ["--grammar_file", grammar_file.replace('.bnf', '_complete_dynamic.bnf'), "--reverse_mapping_target", p])
                                        for p in orderering_preserving_duplicates_elimination(phenotypes)]
        else:
            args: List[Tuple[Any]] = [("scripts/GE_LR_parser.py", ["--grammar_file", grammar_file, "--reverse_mapping_target", p])
                                        for p in orderering_preserving_duplicates_elimination(phenotypes)]
    elif bnf_type == STATICBNF_AS_STRING:
        args: List[Tuple[Any]] = [("scripts/GE_LR_parser.py", ["--grammar_file", grammar_file, "--reverse_mapping_target", p])
                                    for p in orderering_preserving_duplicates_elimination(phenotypes)]
    else:
        raise ValueError(f"bnf_type {bnf_type} unrecognized in parse_genotypes.")
    
    with multiprocessing.Pool(processes=len(args)) as pool:
        genotypes = [r for r in pool.starmap(worker_function, args) if r is not None]
    
    return genotypes


def worker_function(script_path: str, script_args: Tuple[Any]) -> Any:
    try:
        process = subprocess.Popen(["python", script_path] + script_args,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, _ = process.communicate()
        if "Genome" in stdout:
            return stdout[stdout.index('['): stdout.index(']') + 1]
    except:
        pass


def create_txt_foreach_ind(dir_name: str, genotypes: List[List[str]], already_solved: bool, num_iter_solved: int, data_length: int, only_impr: bool) -> None:
    parsed: bool = True
    e: str = "No individuals specified for starter population. "
    if not already_solved and len(genotypes) == 0:
        parsed = False
    base_path = "../seeds/"
    base_path_metadata = "../seeds_metadata/"
    if not os.path.isdir(base_path):
        os.makedirs(base_path)
    if not os.path.isdir(base_path_metadata):
        os.makedirs(base_path_metadata)
    res_dir_path: str = os.path.join(base_path, dir_name)
    if not os.path.isdir(res_dir_path):
        os.makedirs(res_dir_path)
    res_dir_path_metadata: str = os.path.join(base_path_metadata, dir_name)
    if not os.path.isdir(res_dir_path_metadata):
        os.makedirs(res_dir_path_metadata)
    index: int = 1
    
    if only_impr:
        if os.path.exists(os.path.join(res_dir_path_metadata, f"{ALREADY_SOLVED_STRING}{'.txt'}")):
            e += ALREADY_SOLVED_STRING + '.'
            raise Exception(e)
        
        if os.path.exists(os.path.join(res_dir_path_metadata, f"{NOT_PARSED_STRING}{'.txt'}")):
            e += NOT_PARSED_STRING + '.'
            raise Exception(e)

        return
    
    for genotype in genotypes:
        output_path: str = os.path.join(res_dir_path, f"{index}{'.txt'}")
        output_file = open(output_path, 'w')
        output_file.write("Genotype:\n" + genotype)
        output_file.close()
        index += 1
    
    if already_solved:
        e += ALREADY_SOLVED_STRING + '.'
        output_path = os.path.join(res_dir_path_metadata, f"{ALREADY_SOLVED_STRING}{'.txt'}")
        output_file = open(output_path, 'w')
        output_file.write(f'{num_iter_solved}/{data_length}')
        output_file.close()
        raise Exception(e)

    if not parsed:
        e += NOT_PARSED_STRING + '.'
        output_path = os.path.join(res_dir_path_metadata, f"{NOT_PARSED_STRING}{'.txt'}")
        output_file = open(output_path, 'w')
        output_file.write('')
        output_file.close()
        raise Exception(e)


def txt_population(
        json_path: str,
        model_name: str,
        benchmark_name: str,
        benchmark_type: str,
        problem_index: int,
        iterations: int,
        train_size: int,
        test_size: int,
        only_impr: bool,
        grammar_file: str,
        output_dir_name: str,
        dynamic_bnf: str
    ) -> None:
    cwd: str = os.getcwd()
    os.chdir("../PonyGE2/src")
    try:
        phenotypes, already_solved, num_iter_solved, data_length = load_phenotypes_from_json(
            json_path=json_path,
            model_name=model_name,
            benchmark_name=benchmark_name,
            benchmark_type=benchmark_type,
            problem_index=problem_index,
            iterations=iterations,
            train_size=train_size,
            test_size=test_size
        )
        genotypes: List[List[str]] = parse_genotypes(phenotypes, grammar_file, already_solved=already_solved, only_impr=only_impr, dynamic_bnf=dynamic_bnf)
        create_txt_foreach_ind(output_dir_name, genotypes, already_solved, num_iter_solved, data_length, only_impr=only_impr)
    finally:
        os.chdir(cwd)
