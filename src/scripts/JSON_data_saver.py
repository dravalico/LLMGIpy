import os
from datetime import datetime
import json

BASE_PATH: str = "../results/"
FOLDER_NAME: str = str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))


def create_json_file(model_name: str,
                     problems_number: int,
                     iteration: int,
                     model_response: str,
                     tests_results: dict[any, any],
                     error: str = "") -> None:
    if not os.path.isdir(BASE_PATH):
        os.mkdir(BASE_PATH)

    results_folder_path: str = os.path.join(BASE_PATH, FOLDER_NAME)
    if not os.path.isdir(results_folder_path):
        os.mkdir(results_folder_path)

    model_response = model_response.replace("    ", "\t")
    to_save: dict[str, any] = {
        "model_name": model_name,
        "problems_number": problems_number,
        "iteration": iteration,
        "model_response": model_response,
        "results": tests_results if error != "" else error
    }
    json_results = json.dumps(to_save, indent=4)

    filename: str = f"{model_name}{'_problem'}{problems_number}{'.json'}"
    output_file_path: str = os.path.join(results_folder_path, filename)
    if os.path.exists(output_file_path):
        modify_type: str = "a"
    else:
        modify_type: str = "w"
    output_file = open(output_file_path, modify_type)
    output_file.write(json_results + "\n")
    output_file.close()
