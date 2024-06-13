import os
import subprocess
from typing import Any, List, Dict, Tuple
import multiprocessing
from scripts.function_util import orderering_preserving_duplicates_elimination
from scripts.json_data_io import read_json, create_dir_path_string, ALREADY_SOLVED_STRING, NOT_PARSED_STRING


def load_phenotypes_from_json(
        json_path: str,
        model_name: str,
        benchmark_name: str,
        problem_index: int,
        iterations: int,
        train_size: int,
        test_size: int
    ) -> Tuple[List[str], bool, int, int]:
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

    phenotypes: List[str] = []
    data_train_size: int = int(json_file["data_train_size"])
    
    if data_train_size != train_size:
        raise ValueError(f'Declared train_size {train_size} is different from the data_train_size {data_train_size} found in the results.')
    
    already_solved: bool = False
    num_iter_solved: int = 0
    for i in range(0, len(data)):
        final_ind: str = data[i]['final_individual'] if 'final_individual' in data[i] else ''.join([f'def evolve({", ".join(f"v{i}" for i in range(n_inputs))}):', '{:#pass#:}'])
        phenotypes.append(final_ind)
        if 'tests_results' in data[i] and 'passed' in data[i]["tests_results"] and int(data[i]["tests_results"]["passed"]) == train_size:
            num_iter_solved += 1
    if num_iter_solved > 0:
        already_solved = True
    return phenotypes, already_solved, num_iter_solved, len(data)


def parse_genotypes(phenotypes: List[str], grammar_file: str, already_solved: bool, only_impr: bool) -> List[List[str]]:
    if only_impr:
        return []
    if len(phenotypes) == 0:
        e: str = "You must specify at least one individual phenotype."
        raise Exception(e)
    genotypes: List[Any] = []
    args: List[Tuple[Any]] = [("scripts/GE_LR_parser.py", ["--grammar_file", grammar_file, "--reverse_mapping_target", p])
                              for p in orderering_preserving_duplicates_elimination(phenotypes)]
    if not already_solved:
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
        problem_index: int,
        iterations: int,
        train_size: int,
        test_size: int,
        only_impr: bool,
        grammar_file: str,
        output_dir_name: str
    ) -> None:
    cwd: str = os.getcwd()
    os.chdir("../PonyGE2/src")
    try:
        phenotypes, already_solved, num_iter_solved, data_length = load_phenotypes_from_json(
            json_path=json_path,
            model_name=model_name,
            benchmark_name=benchmark_name,
            problem_index=problem_index,
            iterations=iterations,
            train_size=train_size,
            test_size=test_size
        )
        genotypes: List[List[str]] = parse_genotypes(phenotypes, grammar_file, already_solved, only_impr)
        create_txt_foreach_ind(output_dir_name, genotypes, already_solved, num_iter_solved, data_length, only_impr)
    finally:
        os.chdir(cwd)
