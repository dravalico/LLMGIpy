from copy import copy
import os
from typing import Any
from os import getcwd, makedirs, path
from shutil import rmtree

from algorithm.parameters import params
from utilities.stats import trackers


BASE_PATH: str = "../results/"


def create_results_folder_path(base_path: str, params: dict[str, Any], include_seed: bool, make_dirs: bool) -> str:
    if not os.path.isdir(base_path):
        os.mkdir(base_path)

    full_path: str = base_path
    full_path += 'GI' + '/'
    full_path += params['BENCHMARK_NAME'] + '/'
    full_path += params['MODEL_NAME'] + '/'
    
    if isinstance(params['FITNESS_FUNCTION'], str):
        full_path += params['FITNESS_FUNCTION'] + '_' + params['FITNESS_FILE'][:-4] + '_' + f'train{params["NUM_TRAIN_EXAMPLES"]}_test{params["NUM_TEST_EXAMPLES"]}' + '/'
    else:
        full_path += params['FITNESS_FUNCTION'].__class__.__name__ + '_' + params['FITNESS_FILE'][:-4] + '_' + f'train{params["NUM_TRAIN_EXAMPLES"]}_test{params["NUM_TEST_EXAMPLES"]}' + '/'
    
    if isinstance(params['SELECTION'], str):
        full_path += (f'{params["SELECTION"]}{params["TOURNAMENT_SIZE"]}' if params['SELECTION'] == 'tournament' else f'{params["SELECTION"]}') + '_'
    else:
        full_path += (f'{params["SELECTION"].__name__}{params["TOURNAMENT_SIZE"]}' if params['SELECTION'].__name__ == 'tournament' else f'{params["SELECTION"].__name__}') + '_'
    
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
        os.makedirs(results_folder_path)

    return results_folder_path

def save_stats_to_file(stats, end=False):
    """
    Write the results to a results file for later analysis

    :param stats: The stats.stats.stats dictionary.
    :param end: A boolean flag indicating whether or not the evolutionary
    process has finished.
    :return: Nothing.
    """

    if False: # params['VERBOSE'] 
        filename = path.join(create_results_folder_path(BASE_PATH, params, True, True), "stats.tsv")
        savefile = open(filename, 'a')
        for stat in sorted(stats.keys()):
            savefile.write(str(stats[stat]) + "\t")
        savefile.write("\n")
        savefile.close()

    elif end:
        filename = path.join(create_results_folder_path(BASE_PATH, params, True, True), "stats.tsv")
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

    filename = path.join(create_results_folder_path(BASE_PATH, params, True, True), "stats.tsv")
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
    makedirs(params['FILE_PATH'])

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
        path_1 = path.join(getcwd(), "..", "results")

        if not path.isdir(path_1):
            # Create results folder.
            #makedirs(path_1, exist_ok=True)
            pass

        # Set file path to include experiment name.
        params['FILE_PATH'] = path.join(path_1, params['EXPERIMENT_NAME'])

    else:
        # Set file path to results folder.
        params['FILE_PATH'] = path.join(getcwd(), "..", "results")

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
