import os
from datetime import datetime
import json

_BASE_PATH: str = "../results/"
_FOLDER_NAME: str = str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))


def create_and_save_json(filename: str, data: list[dict[str, any]]) -> None:
    if not os.path.isdir(_BASE_PATH):
        os.mkdir(_BASE_PATH)

    results_folder_path: str = os.path.join(_BASE_PATH, _FOLDER_NAME)
    if not os.path.isdir(results_folder_path):
        os.mkdir(results_folder_path)

    json_results = json.dumps(data, indent=4)

    filename: str = f"{filename}{'.json'}"
    output_file_path: str = os.path.join(results_folder_path, filename)
    output_file = open(output_file_path, 'w')
    output_file.write(json_results)
    output_file.close()
