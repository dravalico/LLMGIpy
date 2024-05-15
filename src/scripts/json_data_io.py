import os
import json
from typing import Dict

BASE_PATH: str = "../results/"


def create_and_save_json(filename: str, data: Dict[str, any]) -> str:
    if not os.path.isdir(BASE_PATH):
        os.mkdir(BASE_PATH)

    full_path: str = BASE_PATH
    
    if data['reask']:
        full_path += 'LPLUS' + '/'
    else:
        full_path += 'L' + '/'
    
    full_path += data['problem_benchmark'] + '/'
    full_path += data['model_name'] + '/'

    if data['reask']:
        full_path += 'iter' + str(data['iterations']) + '_rep' + str(data['repeatitions']) + '/'
    else:
        full_path += 'iter' + str(data['iterations']) + '_rep0' + '/'

    full_path += f'train{data["data_train_size"]}_test{data["data_test_size"]}' + '/'

    results_folder_path: str = full_path
    if not os.path.isdir(results_folder_path):
        os.makedirs(results_folder_path)

    json_results = json.dumps(data, indent=4)

    output_file_path: str = os.path.join(results_folder_path, f"{filename}{'.json'}")
    output_file = open(output_file_path, 'w')
    output_file.write(json_results)
    output_file.close()

    return results_folder_path


def read_json(
    model_name: str,
    problem_benchmark: str,
    problem_id: int,
    reask: bool,
    iterations: int,
    repeatitions: int,
    train_size: int,
    test_size: int
) -> dict[str, any]:
    full_path: str = BASE_PATH
    
    if reask:
        full_path += 'LPLUS' + '/'
    else:
        full_path += 'L' + '/'
    
    full_path += problem_benchmark + '/'
    full_path += model_name + '/'

    if reask:
        full_path += 'iter' + str(iterations) + '_rep' + str(repeatitions) + '/'
    else:
        full_path += 'iter' + str(iterations) + '_rep0' + '/'

    full_path += f'train{train_size}_test{test_size}' + '/'

    results_folder_path: str = full_path
    output_file_path: str = os.path.join(results_folder_path, f"{'problem'}{problem_id}{'.json'}")
    
    with open(output_file_path, 'r') as f:
        d: dict[str, any] = json.load(f)
    
    return d