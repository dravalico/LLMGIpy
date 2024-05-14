import os
import json
from typing import Dict

BASE_PATH: str = "../results/"


def create_and_save_json(filename: str, data: Dict[str, any]) -> str:
    if not os.path.isdir(BASE_PATH):
        os.mkdir(BASE_PATH)

    full_path: str = BASE_PATH
    if data['reask']:
        full_path += 'LPLUS' + '/' + 'iter' + str(data['iterations']) + '_rep' + str(data['repeatitions']) + '/'
    else:
        full_path += 'L' + '/' + 'iter' + str(data['iterations']) + '_rep0' + '/'
    if data['remove_non_existing_imports']:
        full_path += 'removenonexistingimports1' + '/'
    else:
        full_path += 'removenonexistingimports0' + '/'
    full_path += data['problem_benchmark'] + '/' + f'train{data['data_train_size']}_test{data['data_test_size']}' + '/'

    results_folder_path: str = full_path
    if not os.path.isdir(results_folder_path):
        os.mkdir(results_folder_path)

    json_results = json.dumps(data, indent=4)

    output_file_path: str = os.path.join(results_folder_path, f"{filename}{'.json'}")
    output_file = open(output_file_path, 'w')
    output_file.write(json_results)
    output_file.close()

    return results_folder_path
