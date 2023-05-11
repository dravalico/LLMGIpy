import os
from datetime import datetime
import json
from typing import List, Dict


def create_and_save_json(filename: str, data: List[Dict[str, any]]) -> str:
    base_path: str = "../results/"
    folder_name: str = str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
    if not os.path.isdir(base_path):
        os.mkdir(base_path)

    results_folder_path: str = os.path.join(base_path, folder_name)
    if not os.path.isdir(results_folder_path):
        os.mkdir(results_folder_path)

    json_results = json.dumps(data, indent=4)

    output_file_path: str = os.path.join(results_folder_path, f"{filename}{'.json'}")
    output_file = open(output_file_path, 'w')
    output_file.write(json_results)
    output_file.close()
    return results_folder_path
