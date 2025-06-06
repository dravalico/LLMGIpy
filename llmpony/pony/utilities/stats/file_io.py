import json
from copy import copy
import os
from typing import Any
from os import getcwd, makedirs, path
from shutil import rmtree

import pandas as pd

from llmpony.pony.algorithm.parameters import params
from llmpony.pony.utilities.stats import trackers


BASE_PATH: str = "PonyGE2/results/"
PONY_CSV_SEPARATOR: str = "\t"


def create_results_folder_path(base_path: str, params: dict[str, Any], include_seed: bool, make_dirs: bool) -> str:
    # What keys are needed to be available in params dict? Here's the list:
    # BENCHMARK_NAME
    # BENCHMARK_TYPE
    # BNF_TYPE
    # MODEL_NAME
    # FITNESS_FUNCTION
    # FITNESS_FILE (.txt extension included)
    # INITIALISATION
    # NUM_TRAIN_EXAMPLES
    # NUM_TEST_EXAMPLES
    # SELECTION
    # TOURNAMENT_SIZE
    # SELECTION_SAMPLE_SIZE
    # CROSSOVER
    # MUTATION
    # POPULATION_SIZE
    # GENERATIONS
    # CROSSOVER_PROBABILITY
    # MUTATION_PROBABILITY
    # PROBLEM_INDEX
    # RANDOM_SEED
    if not os.path.isdir(base_path) and base_path.strip() != '':
        os.mkdir(base_path)

    full_path: str = base_path
    full_path += 'GI' + '/'
    full_path += params['BENCHMARK_NAME'] + '_' + params['BENCHMARK_TYPE'] + '/'
    full_path += params['MODEL_NAME'] + '/'
    
    if isinstance(params['INITIALISATION'], str):
        full_path += params['INITIALISATION'] + '/'
    else:
        full_path += params['INITIALISATION'].__name__ + '/'

    if isinstance(params['FITNESS_FUNCTION'], str):
        full_path += params['FITNESS_FUNCTION'] + '_' + params['FITNESS_FILE'][:-4] + '_' + f'train{params["NUM_TRAIN_EXAMPLES"]}_test{params["NUM_TEST_EXAMPLES"]}' + '_' + params['BNF_TYPE'] + '/'
    else:
        full_path += params['FITNESS_FUNCTION'].__class__.__name__ + '_' + params['FITNESS_FILE'][:-4] + '_' + f'train{params["NUM_TRAIN_EXAMPLES"]}_test{params["NUM_TEST_EXAMPLES"]}' + '_' + params['BNF_TYPE'] + '/'
    
    if isinstance(params['SELECTION'], str):
        full_path += f'{params["SELECTION"]}{params["TOURNAMENT_SIZE"]}' if params['SELECTION'] == 'tournament' else f'{params["SELECTION"]}'
    else:
        full_path += f'{params["SELECTION"].__name__}{params["TOURNAMENT_SIZE"]}' if params['SELECTION'].__name__ == 'tournament' else f'{params["SELECTION"].__name__}'
    full_path += '_'
    full_path += f'selsamplesize{min(params["NUM_TRAIN_EXAMPLES"], params["SELECTION_SAMPLE_SIZE"])}'
    full_path += '_'
    
    if isinstance(params['CROSSOVER'], str) and isinstance(params['MUTATION'], str):
        full_path += f'pop{params["POPULATION_SIZE"]}_gen{params["GENERATIONS"]}_cx{params["CROSSOVER"]}{params["CROSSOVER_PROBABILITY"]}mut{params["MUTATION"]}{params["MUTATION_PROBABILITY"]}' + '/'
    else:
        full_path += f'pop{params["POPULATION_SIZE"]}_gen{params["GENERATIONS"]}_cx{params["CROSSOVER"].__name__}{params["CROSSOVER_PROBABILITY"]}mut{params["MUTATION"].__name__}{params["MUTATION_PROBABILITY"]}' + '/'
    
    if include_seed:
        full_path += f'problem{params["PROBLEM_INDEX"]}' + '_'
        full_path += f'seed{params["RANDOM_SEED"]}' + '/'
    else:
        full_path += f'problem{params["PROBLEM_INDEX"]}' + '/'

    results_folder_path: str = full_path
    if make_dirs and not os.path.isdir(results_folder_path):
        os.makedirs(results_folder_path, exist_ok=True)

    return results_folder_path


def read_ponyge_results(base_path: str, params: dict[str, Any], include_seed: bool) -> dict:
    path: str = create_results_folder_path(base_path=base_path, params=params, include_seed=include_seed, make_dirs=False)
    if not path.endswith('/'):
        path += '/'
    executed_gens: list[int] = sorted([int(file[:file.index('.txt')]) for file in os.listdir(path) if file.endswith('.txt') and file[:file.index('.txt')].isdigit()])
    if len(executed_gens) == 0:
        raise ValueError(f'This run {path} is not available.')
    stats: pd.DataFrame = pd.read_csv(path + 'stats.tsv', sep='\t', header=0)
    res = {'stats': stats, 'gens': []}
    for gen in executed_gens:
        with open(path + str(gen) + '.txt', 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() != '']
        gen_dict = {}
        for i in range(0, len(lines), 2):
            gen_dict[lines[i]] = lines[i + 1]
        res['gens'].append(gen_dict)

    return res


def read_ponyge_results_with_unique_json(base_path: str, params: dict[str, Any], include_seed: bool) -> dict:
    path: str = create_results_folder_path(base_path=base_path, params=params, include_seed=include_seed, make_dirs=False)
    if not path.endswith('/'):
        path += '/'
    with open(path + 'bests.json', 'r') as f:
        bests = json.load(f)
    stats: pd.DataFrame = pd.read_csv(path + 'stats.csv', sep='\t', header=0)
    res = {'stats': stats, 'gens': bests['gens']}

    return res


def save_stats_to_file(stats, end=False):
    """
    Write the results to a results file for later analysis

    :param stats: The stats.stats.stats dictionary.
    :param end: A boolean flag indicating whether or not the evolutionary
    process has finished.
    :return: Nothing.
    """

    if False: # params['VERBOSE'] 
        filename = path.join(create_results_folder_path(BASE_PATH, params, True, True), "stats.csv")
        savefile = open(filename, 'a')
        for stat in sorted(stats.keys()):
            savefile.write(str(stats[stat]) + "\t")
        savefile.write("\n")
        savefile.close()

    elif end:
        filename = path.join(create_results_folder_path(BASE_PATH, params, True, True), "stats.csv")
        savefile = open(filename, 'a')
        for item in trackers.stats_list:
            for stat in sorted(item.keys()):
                savefile.write(str(item[stat]) + "\t")
            savefile.write("\n")
        savefile.close()


def save_stats_headers(stats):
    """
    Saves the headers for all stats in the stats dictionary.

    :param stats: The stats.stats.stats dictionary.
    :return: Nothing.
    """

    filename = path.join(create_results_folder_path(BASE_PATH, params, True, True), "stats.csv")
    savefile = open(filename, 'w')
    for stat in sorted(stats.keys()):
        savefile.write(str(stat) + "\t")
    savefile.write("\n")
    savefile.close()


def save_best_ind_to_file(stats, ind, end=False, name="best", execution_time_in_minutes=None):
    """
    Saves the best individual to a file.

    :param stats: The stats.stats.stats dictionary.
    :param ind: The individual to be saved to file.
    :param end: A boolean flag indicating whether or not the evolutionary
    process has finished.
    :param name: The name of the individual. Default set to "best".
    :return: Nothing.
    """

    filename = path.join(create_results_folder_path(BASE_PATH, params, True, True), (str(name) + ".txt"))
    savefile = open(filename, 'w')
    if execution_time_in_minutes is not None:
        savefile.write("Execution time (min):\n" + str(execution_time_in_minutes) + "\n\n")
    savefile.write("Training Execution time (min):\n" + str(sum(trackers.train_time_list) * (1 / 60)) + "\n\n")
    savefile.write("Generation:\n" + str(stats['gen']) + "\n\n")
    savefile.write("Phenotype:\n" + str(ind.phenotype) + "\n\n")
    savefile.write("Genotype:\n" + str(ind.genome) + "\n")
    savefile.write("Tree:\n" + str(ind.tree) + "\n")
    if hasattr(params['FITNESS_FUNCTION'], "training_test"):
        if True: # end
            savefile.write("\nTraining fitness:\n" + str(ind.training_fitness))
            savefile.write("\nTest fitness:\n" + str(ind.test_fitness))
            if params['FITNESS_FUNCTION'].__class__.__name__ == 'progimpr':
                savefile.write("\nTraining num not passed cases:\n" + str(ind.num_not_passed_cases_train))
                savefile.write("\nTest num not passed cases:\n" + str(ind.num_not_passed_cases_test))
        else:
            savefile.write("\nFitness:\n" + str(ind.fitness))
    else:
        savefile.write("\nFitness:\n" + str(ind.fitness))
    savefile.close()


def save_all_best_individuals_to_json(best_individuals):
    """
    Saves the best individuals to a file.

    :param best_individuals: The best individuals in a list, one element for each generation.
    :return: Nothing.
    """

    filename = path.join(create_results_folder_path(BASE_PATH, params, True, True), "bests.json")
    gens = []

    for i in range(len(best_individuals)):
        ind = best_individuals[i]
        data = dict()

        data["Training Execution time (min)"] = str(sum(trackers.train_time_list[:(i + 1)]) * (1 / 60))
        data["Generation"] = str(i)
        data["Phenotype"] = str(ind.phenotype)
        data["Genotype"] = str(ind.genome)
        data["Tree"] = str(ind.tree)
        data["Training fitness"] = str(ind.training_fitness)
        data["Test fitness"] = str(ind.test_fitness)
        if params['FITNESS_FUNCTION'].__class__.__name__ == 'progimpr':
            data["Training num not passed cases"] = str(ind.num_not_passed_cases_train)
            data["Test num not passed cases"] = str(ind.num_not_passed_cases_test)

        gens.append(data)

    with open(filename, 'w') as f:
        json.dump({'gens': gens}, f, indent=4)


def save_first_front_to_file(stats, end=False, name="first"):
    """
    Saves all individuals in the first front to individual files in a folder.

    :param stats: The stats.stats.stats dictionary.
    :param end: A boolean flag indicating whether or not the evolutionary
                process has finished.
    :param name: The name of the front folder. Default set to "first_front".
    :return: Nothing.
    """

    # Save the file path (we will be over-writing it).
    orig_file_path = copy(params['FILE_PATH'])

    # Define the new file path.
    params['FILE_PATH'] = path.join(orig_file_path, str(name) + "_front")

    # Check if the front folder exists already
    if path.exists(params['FILE_PATH']):
        # Remove previous files.
        rmtree(params['FILE_PATH'])

    # Create front folder.
    makedirs(params['FILE_PATH'], exist_ok=True)

    for i, ind in enumerate(trackers.best_ever):
        # Save each individual in the first front to file.
        save_best_ind_to_file(stats, ind, end, name=str(i))

    # Re-set the file path.
    params['FILE_PATH'] = copy(orig_file_path)


def generate_folders_and_files():
    """
    Generates necessary folders and files for saving statistics and parameters.

    :return: Nothing.
    """

    if params['EXPERIMENT_NAME']:
        # Experiment manager is being used.
        path_1 = path.join("PonyGE2", "results")

        if not path.isdir(path_1):
            # Create results folder.
            #makedirs(path_1, exist_ok=True)
            pass

        # Set file path to include experiment name.
        params['FILE_PATH'] = path.join(path_1, params['EXPERIMENT_NAME'])

    else:
        # Set file path to results folder.
        params['FILE_PATH'] = path.join("PonyGE2", "results")

    # Generate save folders
    if not path.isdir(params['FILE_PATH']):
        #makedirs(params['FILE_PATH'], exist_ok=True)
        pass

    if not path.isdir(path.join(params['FILE_PATH'], str(params['TIME_STAMP']))):
        #makedirs(path.join(params['FILE_PATH'], str(params['TIME_STAMP'])), exist_ok=True)
        pass

    params['FILE_PATH'] = path.join(params['FILE_PATH'], str(params['TIME_STAMP']))

    save_params_to_file()


def save_params_to_file():
    """
    Save evolutionary parameters in a parameters.txt file.

    :return: Nothing.
    """

    # Generate file path and name.
    filename = path.join(create_results_folder_path(BASE_PATH, params, True, True), "parameters.txt")
    savefile = open(filename, 'w')

    # Justify whitespaces for pretty printing/saving.
    col_width = max(len(param) for param in params.keys())

    for param in sorted(params.keys()):
        # Create whitespace buffer for pretty printing/saving.
        spaces = [" " for _ in range(col_width - len(param))]
        savefile.write(str(param) + ": " + "".join(spaces) +
                       str(params[param]) + "\n")

    savefile.close()
