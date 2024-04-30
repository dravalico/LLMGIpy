import json
import pandas as pd
from pandas import DataFrame
import statistics
import os
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
from typing import List, Any, Tuple, Dict
from datetime import datetime


BASE_PATH: str = "../processed_results/"
FOLDER_NAME: str = str(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))


def load_data_from_json(json_path: str) -> Any:
    with open(json_path, 'r') as json_file:
        data: Any = json.load(json_file)
    return data


def calculate_statistics(values, size) -> Tuple[float]:
    try:
        mean: float = round(statistics.mean(values) * 100 / size, 3)
    except:
        mean = 0.0
    try:
        median: float = round(statistics.median(values) / size, 2) # TODO modified
    except:
        median = 0.0
    try:
        mode: float = round(statistics.mode(values) * 100 / size, 3)
    except:
        mode = 0.0
    try:
        variance: float = round(statistics.stdev(values) * 100 / size, 3)
    except:
        variance = 0.0
    return mean, mode, median, variance


def create_statistics_table(data) -> Dict[str, Any]:
    table: Dict[str, Any] = {}
    problem_name: str = data["problem_name"]
    model_name: str = data["model_name"]
    if problem_name not in table:
        table[problem_name] = {}
    if model_name not in table[problem_name]:
        table[problem_name][model_name] = {"μ, mode, med, σ": []}
    json_data: List[Dict[str, Any]] = data["data"]
    statistics_data: List[int] = []
    for item in json_data:
        try:
            statistics_data.append(item["tests_results"]["passed"])
        except:
            pass
    table[problem_name][model_name]["μ, mode, med, σ"] = calculate_statistics(statistics_data, data["data_test_size"])
    return table


def combine_dictionaries(dictionaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    combined_dicts: Dict[str, Any] = {}
    for data in dictionaries:
        for key, value in data.items():
            for model, stats in value.items():
                if model not in combined_dicts:
                    combined_dicts[model] = {}
                combined_dicts[model][key] = stats
    return combined_dicts


def save_table_to_csv(table: Dict[str, Any], csv_path: str) -> None:
    df: DataFrame = pd.DataFrame.from_dict({(i, j): table[i][j]
                                            for i in table.keys()
                                            for j in table[i].keys()},
                                           orient="index")
    df.index.names = ["Problem", "Model"]
    df.to_csv(csv_path)


def create_csv_statistics(jsons_dirs_path: List[str]) -> str:
    data: List[Dict[str, Any]] = []
    for jsons_dir_path in jsons_dirs_path:
        for filename in [f for f in listdir(jsons_dir_path) if isfile(join(jsons_dir_path, f))]:
            data1 = load_data_from_json(join(jsons_dir_path + '/' + filename))
            statistics_table: Dict[str, Any] = create_statistics_table(data1)
            data.append(statistics_table)
    if not os.path.isdir(BASE_PATH):
        os.mkdir(BASE_PATH)
    results_folder_path: str = os.path.join(BASE_PATH, FOLDER_NAME)
    if not os.path.isdir(results_folder_path):
        os.mkdir(results_folder_path)
    csv_path: str = os.path.join(results_folder_path, "statistics_table.csv")
    save_table_to_csv(combine_dictionaries(data), csv_path)
    return csv_path


def create_csv_table_fig(csv_path: str) -> None:
    df: DataFrame = pd.read_csv(csv_path)
    pivot_table: DataFrame = df.pivot(index='Model', columns='Problem')
    fig, ax = plt.subplots()
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=pivot_table.values,
                     rowLabels=pivot_table.index,
                     colLabels=pivot_table.columns,
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.30] * len(pivot_table.columns))
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    fig.set_size_inches(10, 10)
    plt.savefig(os.path.join(BASE_PATH, FOLDER_NAME, "table_fig.png"))


def main():  # TODO remove it
    path: str = create_csv_statistics(["/mnt/data/gpinna/damiano_pony/LLMGIpy/json_data/jsons_results_psb2/results_psb2/ChG", "/mnt/data/gpinna/damiano_pony/LLMGIpy/json_data/jsons_results_psb2/results_psb2/G4"])
    create_csv_table_fig(path)


if __name__ == "__main__":
    main()
