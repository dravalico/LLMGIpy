import os
import json
import subprocess
from typing import Any, List, Dict, Tuple
from subprocess import CompletedProcess
from scripts.function_util import extract_function_name
import multiprocessing
import random


def load_phenotypes_from_json(json_path: str) -> List[str]:
    with open(json_path, 'r') as json_file:
        json_file: Any = json.load(json_file)
    data: List[Dict[str, Any]] = json_file["data"]
    phenotypes: List[str] = []
    for i in range(0, len(data)):
        phenotypes.append(data[i]["individual"])
    return phenotypes


def parse_genotypes(phenotypes: List[str], grammar_file: str) -> List[str]:
    if len(phenotypes) == 0:
        e: str = "You must specify at least one individual phenotype."
        raise Exception(e)
    genotypes: List[str] = []
    for phenotype in list(set(phenotypes)):  # NOTE takes only different phenotypes
        try:
            phenotype = phenotype.replace(extract_function_name(phenotype), "evolve")  # NOTE hardcoded
            process_res: CompletedProcess = subprocess.run(
                ["python", "scripts/GE_LR_parser.py", "--grammar_file",
                    grammar_file, "--reverse_mapping_target", phenotype],
                capture_output=True
            )
            if process_res.returncode == 0:
                output: str = str(process_res.stdout)
                print(output)
                if "Genome" in output:
                    genotypes.append(output[output.index('['): output.index(']') + 1])
        except Exception as e:
            pass
    return genotypes


def parse_genotypes_new(phenotypes: List[str], grammar_file: str) -> List[str]:
    if len(phenotypes) == 0:
        e: str = "You must specify at least one individual phenotype."
        raise Exception(e)
    genotypes: List[Any] = []
    args: List[Tuple[Any]] = [("scripts/GE_LR_parser.py", ["--grammar_file", grammar_file, "--reverse_mapping_target", p])
                              for p in list(set(phenotypes))]
    with multiprocessing.Pool(processes=len(args)) as pool:
        genotypes = pool.starmap(worker_function, args)
    return genotypes


def worker_function(script_path: str, script_args: Tuple[Any]) -> Any:
    rand = random.uniform(1.0, 2000.0)
    try:
        process = subprocess.Popen(["python", script_path] + script_args, stdout=subprocess.PIPE, text=True)
        with open(f"/mnt/data/dravalico/workspace/a", 'a') as file:
            file.write(f"iniziato -> {str(rand)}\n")
        stdout, _ = process.communicate()
        with open(f"/mnt/data/dravalico/workspace/a", 'a') as file:
            file.write(f"finito -> {str(rand)}\n")
            file.write(str(stdout) + '\n')
        if "Genome" in stdout:
            return stdout[stdout.index('['): stdout.index(']') + 1]
    except:
        with open(f"/mnt/data/dravalico/workspace/a", 'a') as file:
            file.write(f"exception -> {str(rand)}\n")
        pass


def create_txt_foreach_ind(dir_name: str, genotypes: List[str]) -> None:
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
        res: List[str] = load_phenotypes_from_json(json_path)
        res = parse_genotypes_new(res, grammar_file)
        create_txt_foreach_ind(output_dir_name, res)
    finally:
        os.chdir(cwd)
