from random import sample
from random import shuffle
import random
import sys
from algorithm.parameters import params
from utilities.fitness.get_data import read_dataset_input_output_from_txt_with_inval_outval_as_str_list
from utilities.algorithm.NSGA2 import compute_pareto_metrics, \
    crowded_comparison_operator


def selection(population):
    """
    Perform selection on a population in order to select a population of
    individuals for variation.

    :param population: input population
    :return: selected population
    """

    return params['SELECTION'](population)


def tournament(population):
    """
    Given an entire population, draw <tournament_size> competitors randomly and
    return the best. Only valid individuals can be selected for tournaments.

    :param population: A population from which to select individuals.
    :return: A population of the winners from tournaments.
    """

    # Initialise list of tournament winners.
    winners = []

    # The flag "INVALID_SELECTION" allows for selection of invalid individuals.
    if params['INVALID_SELECTION']:
        available = population
    else:
        available = [i for i in population if not i.invalid]

    while len(winners) < params['GENERATION_SIZE']:
        # Randomly choose TOURNAMENT_SIZE competitors from the given
        # population. Allows for re-sampling of individuals.
        competitors = sample(available, params['TOURNAMENT_SIZE'])

        # Return the single best competitor.
        winners.append(max(competitors))

    # Return the population of tournament winners.
    return winners


def lexicase(population):
    """
    Given an entire population, return the best individuals from the population according to a lexicase selection.
    Only valid individuals can be selected for selections.

    :param population: A population from which to select individuals.
    :return: A population of the winners from selections.
    """

    # Initialise list of selection winners.
    winners = []

    # The flag "INVALID_SELECTION" allows for selection of invalid individuals.
    if params['INVALID_SELECTION']:
        available = population
    else:
        available = [i for i in population if not i.invalid]

    worst_fitness = sys.maxsize
    if params['FITNESS_FUNCTION'].maximise:
        worst_fitness = -sys.maxsize    

    dataset_dict = read_dataset_input_output_from_txt_with_inval_outval_as_str_list('progsys', 'TRAIN')
    n_samples = len(dataset_dict['out'])
    data_indices = list(range(n_samples))
    errors_for_each_ind = [i.errors if i.errors is not None else [worst_fitness]*n_samples for i in available]

    if params['FITNESS_FUNCTION'].maximise:
        errors_for_each_ind = [[-aaa for aaa in er_] for er_ in errors_for_each_ind]
    
    for _ in range(params['GENERATION_SIZE']):
        curr_data_indices = [data_ind for data_ind in data_indices]
        shuffle(curr_data_indices)
        competitors = {i: available[i] for i in range(len(available))}
        for i in range(n_samples):
            idx = curr_data_indices[i]
            comp_error = {key: errors_for_each_ind[key][idx] for key in competitors.keys()}
            best_val = min(comp_error.items(), key=lambda x: x[1])[1]
            competitors = {key: competitors[key] for key in competitors.keys() if comp_error[key] == best_val}
            if len(competitors) == 1:
                break
        final_competitors = sorted(list(competitors.keys()))
        winners.append( available[ final_competitors[ int(random.random()*len(final_competitors)) ] ] )
    # Return the population of selection winners.
    return winners


def truncation(population):
    """
    Given an entire population, return the best <proportion> of them.

    :param population: A population from which to select individuals.
    :return: The best <proportion> of the given population.
    """

    # Sort the original population.
    population.sort(reverse=True)

    # Find the cutoff point for truncation.
    cutoff = int(len(population) * float(params['SELECTION_PROPORTION']))

    # Return the best <proportion> of the given population.
    return population[:cutoff]


def nsga2_selection(population):
    """Apply NSGA-II selection operator on the *population*. Usually, the
    size of *population* will be larger than *k* because any individual
    present in *population* will appear in the returned list at most once.
    Having the size of *population* equals to *k* will have no effect other
    than sorting the population according to their front rank. The
    list returned contains references to the input *population*. For more
    details on the NSGA-II operator see [Deb2002]_.
    
    :param population: A population from which to select individuals.
    :returns: A list of selected individuals.
    .. [Deb2002] Deb, Pratab, Agarwal, and Meyarivan, "A fast elitist
       non-dominated sorting genetic algorithm for multi-objective
       optimization: NSGA-II", 2002.
    """

    selection_size = params['GENERATION_SIZE']
    tournament_size = params['TOURNAMENT_SIZE']

    # Initialise list of tournament winners.
    winners = []

    # The flag "INVALID_SELECTION" allows for selection of invalid individuals.
    if params['INVALID_SELECTION']:
        available = population
    else:
        available = [i for i in population if not i.invalid]

    # Compute pareto front metrics.
    pareto = compute_pareto_metrics(available)

    while len(winners) < selection_size:
        # Return the single best competitor.
        winners.append(pareto_tournament(available, pareto, tournament_size))

    return winners


def pareto_tournament(population, pareto, tournament_size):
    """
    The Pareto tournament selection uses both the pareto front of the
    individual and the crowding distance.

    :param population: A population from which to select individuals.
    :param pareto: The pareto front information.
    :param tournament_size: The size of the tournament.
    :return: The selected individuals.
    """

    # Initialise no best solution.
    best = None

    # Randomly sample *tournament_size* participants.
    participants = sample(population, tournament_size)

    for participant in participants:
        if best is None or crowded_comparison_operator(participant, best,
                                                       pareto):
            best = participant

    return best


# Set attributes for all operators to define multi-objective operators.
nsga2_selection.multi_objective = True
