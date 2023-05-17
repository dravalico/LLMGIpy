import os
from datetime import datetime
import json
from typing import List, Dict

BASE_PATH: str = "../results/"
FOLDER_NAME: str = str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))


def create_and_save_json(filename: str, data: List[Dict[str, any]]) -> None:
    if not os.path.isdir(BASE_PATH):
        os.mkdir(BASE_PATH)

    results_folder_path: str = os.path.join(BASE_PATH, FOLDER_NAME)
    if not os.path.isdir(results_folder_path):
        os.mkdir(results_folder_path)

    json_results = json.dumps(data, indent=4)

    output_file_path: str = os.path.join(results_folder_path, f"{filename}{'.json'}")
    output_file = open(output_file_path, 'w')
    output_file.write(json_results)
    output_file.close()


def get_results_dir_path() -> str:
    return os.path.abspath(os.path.join(BASE_PATH, FOLDER_NAME))
