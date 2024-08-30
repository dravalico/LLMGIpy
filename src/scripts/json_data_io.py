import os
import json
from typing import Dict

BASE_PATH: str = "../llm_results/"
ALREADY_SOLVED_STRING: str = 'ALREADY_SOLVED'
NOT_PARSED_STRING: str = 'NOT_PARSED'


def create_and_save_json(filename: str, data: Dict[str, any]) -> str:
    if not os.path.isdir(BASE_PATH):
        os.mkdir(BASE_PATH)

    full_path: str = BASE_PATH
    
    if data['reask']:
        full_path += 'LPLUS' + '/'
    else:
        full_path += 'L' + '/'
    
    full_path += data['problem_benchmark'] + '_' + data['problem_benchmark_type'] + '/'
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


def create_dir_path_string(
    full_path: str,
    model_name: str,
    problem_benchmark: str,
    problem_benchmark_type: str,
    problem_id: int,
    reask: bool,
    iterations: int,
    repeatitions: int,
    train_size: int,
    test_size: int
) -> str:
    if full_path is None or (full_path is not None and full_path.strip() == ''):
        full_path = BASE_PATH
    
    if reask:
        full_path += 'LPLUS' + '/'
    else:
        full_path += 'L' + '/'
    
    full_path += problem_benchmark + '_' + problem_benchmark_type + '/'
    full_path += model_name + '/'

    if reask:
        full_path += 'iter' + str(iterations) + '_rep' + str(repeatitions) + '/'
    else:
        full_path += 'iter' + str(iterations) + '_rep0' + '/'

    full_path += f'train{train_size}_test{test_size}' + '/'

    results_folder_path: str = full_path
    output_file_path: str = os.path.join(results_folder_path, f"{'problem'}{problem_id}{'.json'}")
    
    return output_file_path


def read_json(
    full_path: str,
    model_name: str,
    problem_benchmark: str,
    problem_benchmark_type: str,
    problem_id: int,
    reask: bool,
    iterations: int,
    repeatitions: int,
    train_size: int,
    test_size: int
) -> dict[str, any]:
    
    output_file_path: str = create_dir_path_string(
        full_path=full_path,
        model_name=model_name,
        problem_benchmark=problem_benchmark,
        problem_benchmark_type=problem_benchmark_type,
        problem_id=problem_id,
        reask=reask,
        iterations=iterations,
        repeatitions=repeatitions,
        train_size=train_size,
        test_size=test_size
    )
    
    with open(output_file_path, 'r') as f:
        d: dict[str, any] = json.load(f)
    
    return d
