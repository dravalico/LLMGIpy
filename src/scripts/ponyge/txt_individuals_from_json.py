import os
import json
import subprocess
from typing import Any, List, Dict
from subprocess import CompletedProcess
from scripts.function_util import extract_function_name


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
            output: str = str(process_res.stdout)
            if "Genome" in output:
                genotypes.append(output[output.index('['): output.index(']') + 1])
        except:
            pass
    return genotypes


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
        res = parse_genotypes(res, grammar_file)
        create_txt_foreach_ind(output_dir_name, res)
    finally:
        os.chdir(cwd)
