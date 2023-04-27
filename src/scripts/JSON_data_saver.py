import os
from datetime import datetime
import json

BASE_PATH: str = "../results/"
FOLDER_NAME: str = str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))


def create_json_file(model_name: str,
                     problem_name: str,
                     problem_number: int,
                     data: list[dict[str, any]]) -> None:
    if not os.path.isdir(BASE_PATH):
        os.mkdir(BASE_PATH)

    results_folder_path: str = os.path.join(BASE_PATH, FOLDER_NAME)
    if not os.path.isdir(results_folder_path):
        os.mkdir(results_folder_path)

    to_save: dict[str, any] = {
        "model_name": model_name,
        "problem_name": problem_name,
        "problems_number": problem_number,
        "data": data
    }
    json_results = json.dumps(to_save, indent=4)

    filename: str = f"{model_name}{'_problem'}{problem_number}{'.json'}"
    output_file_path: str = os.path.join(results_folder_path, filename)
    output_file = open(output_file_path, 'w')
    output_file.write(json_results)
    output_file.close()
