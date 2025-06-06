from multiprocessing import Pool
import time
from llmpony.pony.algorithm.parameters import params
from llmpony.pony.fitness.evaluation import evaluate_fitness
from llmpony.pony.operators.initialisation import initialisation
from llmpony.pony.stats.stats import get_stats, stats
from llmpony.pony.utilities.algorithm.initialise_run import pool_init
from llmpony.pony.utilities.stats import trackers


def search_loop():
    """
    This is a standard search process for an evolutionary algorithm. Loop over
    a given number of generations.

    :return: The final population after the evolutionary process has run for
    the specified number of generations.
    """

    if params['MULTICORE']:
        # initialize pool once, if multi-core is enabled
        params['POOL'] = Pool(processes=params['CORES'], initializer=pool_init,
                              initargs=(params,))  # , maxtasksperchild=1)

    # Initialise population
    start_time = time.time()
    individuals = initialisation(params['POPULATION_SIZE'])
    end_time = time.time()

    initialization_time = end_time - start_time
    
    # Evaluate initial population
    individuals, time_slot = evaluate_fitness(individuals)
    time_slot = time_slot + initialization_time
    trackers.train_time_list.append(time_slot)
    
    # Generate statistics for run so far
    get_stats(individuals)

    # Traditional GE
    for generation in range(1, (params['GENERATIONS'] + 1)):
        stats['gen'] = generation

        # New generation
        individuals = params['STEP'](individuals)
        if trackers.best_ever.fitness == 0 or trackers.best_ever.fitness == [0, 0.0] or trackers.best_ever.fitness == "[0, 0.0]":  # STOPPING CRITERION
            break

    if params['MULTICORE']:
        # Close the workers pool (otherwise they'll live on forever).
        params['POOL'].close()

    return individuals


def search_loop_from_state():
    """
    Run the evolutionary search process from a loaded state. Pick up where
    it left off previously.

    :return: The final population after the evolutionary process has run for
    the specified number of generations.
    """

    individuals = trackers.state_individuals

    if params['MULTICORE']:
        # initialize pool once, if multi-core is enabled
        params['POOL'] = Pool(processes=params['CORES'], initializer=pool_init,
                              initargs=(params,))  # , maxtasksperchild=1)

    # Traditional GE
    for generation in range(stats['gen'] + 1, (params['GENERATIONS'] + 1)):
        stats['gen'] = generation

        # New generation
        individuals = params['STEP'](individuals)

    if params['MULTICORE']:
        # Close the workers pool (otherwise they'll live on forever).
        params['POOL'].close()

    return individuals
