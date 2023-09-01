import os
import json
import subprocess
from typing import Any, List, Dict, Tuple
import multiprocessing


def load_phenotypes_from_json(json_path: str) -> List[str]:
    with open(json_path, 'r') as json_file:
        json_file: Any = json.load(json_file)
    data: List[Dict[str, Any]] = json_file["data"]
    phenotypes: List[str] = []
    test_cases: str = json_file["data_test_size"]
    for i in range(0, len(data)):
        if data[i]["tests_results"]["passed"] != test_cases:
            phenotypes.append(data[i]["final_individual"])
    return phenotypes


def parse_genotypes(phenotypes: List[str], grammar_file: str) -> List[List[str]]:
    if len(phenotypes) == 0:
        e: str = "You must specify at least one individual phenotype."
        raise Exception(e)
    genotypes: List[Any] = []
    args: List[Tuple[Any]] = [("scripts/GE_LR_parser.py", ["--grammar_file", grammar_file, "--reverse_mapping_target", p])
                              for p in list(set(phenotypes))]
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


def create_txt_foreach_ind(dir_name: str, genotypes: List[List[str]]) -> None:
    if len(genotypes) == 0:
        e: str = "No individuals specified for starter population."
        raise Exception(e)
    base_path = "../seeds/"
    if not os.path.isdir(base_path):
        os.mkdir(base_path)
    res_dir_path: str = os.path.join(base_path, dir_name)
    if not os.path.isdir(res_dir_path):
        os.mkdir(res_dir_path)
    index: int = 1
    for genotype in genotypes:
        output_path: str = os.path.join(res_dir_path, f"{index}{'.txt'}")
        output_file = open(output_path, 'w')
        output_file.write("Genotype:\n" + genotype)
        output_file.close()
        index += 1


def txt_population(json_path: str,  grammar_file: str, output_dir_name: str) -> None:
    cwd: str = os.getcwd()
    os.chdir("../PonyGE2/src")
    try:
        phenotypes: List[str] = load_phenotypes_from_json(json_path)
        genotypes: List[List[str]] = parse_genotypes(phenotypes, grammar_file)
        create_txt_foreach_ind(output_dir_name, genotypes)
    finally:
        os.chdir(cwd)
