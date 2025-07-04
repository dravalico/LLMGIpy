import os
import random

import numpy as np
import warnings
import time
from copy import deepcopy
from llmpony.pony.fitness.progimpr import progimpr
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from llmpony.pony.algorithm.parameters import params
from llmpony.pony.stats.stats import stats
from llmpony.pony.utilities.stats.trackers import cache, cache_test_set, cache_levi_errors, runtime_error_cache, train_time_list
from llmpony.pony.utilities.algorithm.parallel import process_pool_parallelize, thread_pool_parallelize, fake_parallelize


def insert_elements_random_locations(A, B):
    if len(B) > len(A):
        raise ValueError("List B is longer than list A")

    # Choose distinct random indices in A
    indices = random.sample(range(len(A)), len(B))

    # Shuffle B to randomize element positions (optional)
    random.shuffle(B)

    # Create a copy to avoid modifying A in-place
    A_new = A[:]

    for idx, val in zip(indices, B):
        A_new[idx] = val

    return A_new


def evaluate_fitness(individuals):
    """
    Evaluate an entire population of individuals. Invalid individuals are given
    a default bad fitness. If params['CACHE'] is specified then individuals
    have their fitness stored in a dictionary called utilities.trackers.cache.
    Dictionary keys are the string of the phenotype.
    There are currently three options for use with the cache:
        1. If params['LOOKUP_FITNESS'] is specified (default case if
           params['CACHE'] is specified), individuals which have already been
           evaluated have their previous fitness read directly from the cache,
           thus saving fitness evaluations.
        2. If params['LOOKUP_BAD_FITNESS'] is specified, individuals which
           have already been evaluated are given a default bad fitness.
        3. If params['MUTATE_DUPLICATES'] is specified, individuals which
           have already been evaluated are mutated to produce new unique
           individuals which have not been encountered yet by the search
           process.

    :param individuals: A population of individuals to be evaluated.
    :return: A population of fully evaluated individuals along with the time taken to eval individuals on the training set.
    """

    results, pool = [], None

    if params['MULTICORE']:
        pool = params['POOL']

    almost_new_individuals = []

    start_time = time.time()
    for name, ind in enumerate(individuals):
        ind.name = name

        # Iterate over all individuals in the population.
        if ind.invalid:
            # Invalid individuals cannot be evaluated and are given a bad
            # default fitness.
            ind.fitness = params['FITNESS_FUNCTION'].default_fitness
            ind.levi_test_fitness = params['FITNESS_FUNCTION'].default_fitness
            ind.levi_errors = None
            stats['invalids'] += 1

        else:
            eval_ind = True

            # Valid individuals can be evaluated.
            if params['CACHE'] and ind.phenotype in cache and ind.phenotype in cache_test_set and ind.phenotype in cache_levi_errors:
                # The individual has been encountered before in
                # the utilities.trackers.cache.

                if params['LOOKUP_FITNESS']:
                    # Set the fitness as the previous fitness from the
                    # cache.
                    ind.fitness = cache[ind.phenotype]
                    ind.levi_test_fitness = cache_test_set[ind.phenotype]
                    ind.levi_errors = cache_levi_errors[ind.phenotype]
                    eval_ind = False

                elif params['LOOKUP_BAD_FITNESS']:
                    # Give the individual a bad default fitness.
                    ind.fitness = params['FITNESS_FUNCTION'].default_fitness
                    ind.levi_test_fitness = params['FITNESS_FUNCTION'].default_fitness
                    ind.levi_errors = None
                    eval_ind = False

                elif params['MUTATE_DUPLICATES']:
                    # Mutate the individual to produce a new phenotype
                    # which has not been encountered yet.
                    count = 0
                    while (not ind.phenotype) or ind.phenotype in cache:
                        ind = params['MUTATION'](ind) if params['MUTATION'].__name__ not in ("subtree", "light_subtree") else params['MUTATION'](ind, 1.0)
                        stats['regens'] += 1
                        count += 1
                        if count > params['MUTATE_DUPLICATES_TRIALS']:
                            # If the individual has been mutated MUTATE_DUPLICATES_TRIALS times
                            # and still has a phenotype which is in the cache,
                            # then just give it a bad fitness.
                            ind.fitness = params['FITNESS_FUNCTION'].default_fitness
                            ind.levi_test_fitness = params['FITNESS_FUNCTION'].default_fitness
                            ind.levi_errors = None
                            eval_ind = False
                            break

                    # Need to overwrite the current individual in the pop.
                    individuals[name] = ind
                    ind.name = name

            #if eval_ind:
                #results = eval_or_append(ind, results, pool)
            almost_new_individuals.append((ind, eval_ind))

    pop_size = params['POPULATION_SIZE']
    init_seed_ind = [(abc, False if stats['gen'] > 1 else True) for abc in params['SEED_INDIVIDUALS']]
    if len(almost_new_individuals) >= pop_size:
        almost_new_individuals = insert_elements_random_locations(almost_new_individuals, init_seed_ind)
    else:
        count = 0
        all_params_inserted = False
        while len(almost_new_individuals) < pop_size:
            almost_new_individuals.append(init_seed_ind[count])
            count = (count + 1) % len(init_seed_ind)
            if count == 0:
                all_params_inserted = True
        if not all_params_inserted:
            almost_new_individuals = insert_elements_random_locations(almost_new_individuals, init_seed_ind[count:])

    try:
        new_individuals = process_pool_parallelize(
            eval_or_append,
            [{'index': i, 'ind': deepcopy(almost_new_individuals[i][0]), 'results': [], 'pool': None, 'eval_ind': almost_new_individuals[i][1]} for i in range(len(almost_new_individuals))],
            num_workers=os.cpu_count() // 2,
            chunksize=1,
            timeout=None
        )
    except (RuntimeError, IOError) as e:
        new_individuals = fake_parallelize(
            eval_or_append,
            [{'index': i, 'ind': deepcopy(almost_new_individuals[i][0]), 'results': [], 'pool': None, 'eval_ind': almost_new_individuals[i][1]} for i in range(len(almost_new_individuals))],
            num_workers=os.cpu_count(),
            chunksize=1,
            timeout=None
        )
    end_time = time.time()
    time_slot = end_time - start_time

    almost_new_individuals_2 = []
    for i in range(len(new_individuals)):
        index, train_fitness, levi_errors = new_individuals[i]
        ind, eval_ind = almost_new_individuals[index]
        ind.fitness = train_fitness
        ind.levi_errors = levi_errors
        almost_new_individuals_2.append((ind, eval_ind))

    ############################################################

    try:
        new_individuals_2 = process_pool_parallelize(
            eval_or_append_test,
            [{'index': i, 'ind': deepcopy(almost_new_individuals_2[i][0]), 'results': [], 'pool': None, 'eval_ind': almost_new_individuals_2[i][1]} for i in range(len(almost_new_individuals_2))],
            num_workers=os.cpu_count() // 2,
            chunksize=1,
            timeout=None
        )
    except (RuntimeError, IOError) as e:
        new_individuals_2 = fake_parallelize(
            eval_or_append_test,
            [{'index': i, 'ind': deepcopy(almost_new_individuals_2[i][0]), 'results': [], 'pool': None, 'eval_ind': almost_new_individuals_2[i][1]} for i in range(len(almost_new_individuals_2))],
            num_workers=os.cpu_count(),
            chunksize=1,
            timeout=None
        )

    brand_new_individuals = []
    for i in range(len(new_individuals_2)):
        index, test_fitness = new_individuals_2[i]
        ind, eval_ind = almost_new_individuals_2[index]
        ind.levi_test_fitness = test_fitness
        brand_new_individuals.append((ind, eval_ind))

    ############################################################

    for ind, eval_ind in brand_new_individuals:
        if eval_ind:
            update_ind_cache(ind)

    if params['MULTICORE']:
        for result in results:
            # Execute all jobs in the pool.
            ind = result.get()

            # Set the fitness of the evaluated individual by placing the
            # evaluated individual back into the population.
            individuals[ind.name] = ind

            # Add the evaluated individual to the cache.
            cache[ind.phenotype] = ind.fitness
            cache_test_set[ind.phenotype] = ind.levi_test_fitness
            cache_levi_errors[ind.phenotype] = ind.levi_errors

            # Check if individual had a runtime error.
            if ind.runtime_error:
                runtime_error_cache.append(ind.phenotype)

    return [ind for ind, _ in brand_new_individuals], time_slot


def eval_or_append(index, ind, results, pool, eval_ind=True):
    """
    Evaluates an individual if sequential evaluation is being used. If
    multi-core parallel evaluation is being used, adds the individual to the
    pool to be evaluated.

    :param ind: An individual to be evaluated.
    :param results: A list of individuals to be evaluated by the multicore
    pool of workers.
    :param pool: A pool of workers for multicore evaluation.
    :param eval_ind: A bool telling whether to evaluate the individual from scratch or not.
    :return: The evaluated individual or the list of individuals to be
    evaluated.
    """

    train_fitness = ind.fitness
    levi_errors = ind.levi_errors

    if eval_ind:
        # Evaluate the individual.
        try:
            temp_fitness_class_instance = progimpr()
            train_fitness = temp_fitness_class_instance(ind, dist='training')
            levi_errors = ind.levi_errors
        except Exception as e:
            pass
    
    return index, train_fitness, levi_errors


def eval_or_append_test(index, ind, results, pool, eval_ind=True):
    """
    Evaluates an individual if sequential evaluation is being used. If
    multi-core parallel evaluation is being used, adds the individual to the
    pool to be evaluated.

    :param ind: An individual to be evaluated.
    :param results: A list of individuals to be evaluated by the multicore
    pool of workers.
    :param pool: A pool of workers for multicore evaluation.
    :param eval_ind: A bool telling whether to evaluate the individual from scratch or not.
    :return: The evaluated individual or the list of individuals to be
    evaluated.
    """

    test_fitness = ind.levi_test_fitness

    if eval_ind:
        # Evaluate the individual.
        try:
            temp_fitness_class_instance = progimpr()
            test_fitness = temp_fitness_class_instance(ind, dist='test')
        except Exception as e:
            pass
    
    return index, test_fitness


def update_ind_cache(ind):
    # Check if individual had a runtime error.
    if ind.runtime_error:
        runtime_error_cache.append(ind.phenotype)

    if params['CACHE']:
        # The phenotype string of the individual does not appear
        # in the cache, it must be evaluated and added to the
        # cache.

        if ( 
            (isinstance(ind.fitness, list) and not
        any([np.isnan(i) for i in ind.fitness])) or \
                (not isinstance(ind.fitness, list) and not
                np.isnan(ind.fitness)) 
            ) and \
            (
                (isinstance(ind.levi_test_fitness, list) and not
        any([np.isnan(i) for i in ind.levi_test_fitness])) or \
                (not isinstance(ind.levi_test_fitness, list) and not
                np.isnan(ind.levi_test_fitness))
            ) and \
                ( 
                    ind.levi_errors is None or (ind.levi_errors is not None and isinstance(ind.levi_errors, list))
                ):
            # All fitnesses are valid.
            cache[ind.phenotype] = ind.fitness
            cache_test_set[ind.phenotype] = ind.levi_test_fitness
            cache_levi_errors[ind.phenotype] = ind.levi_errors
