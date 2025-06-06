from llmpony.pony.fitness.evaluation import evaluate_fitness
from llmpony.pony.operators.crossover import crossover
from llmpony.pony.operators.mutation import mutation
from llmpony.pony.operators.replacement import replacement, steady_state
from llmpony.pony.operators.selection import selection
from llmpony.pony.stats.stats import get_stats
import time
from llmpony.pony.utilities.stats import trackers


def step(individuals):
    """
    Runs a single generation of the evolutionary algorithm process:
        Selection
        Variation
        Evaluation
        Replacement
    
    :param individuals: The current generation, upon which a single
    evolutionary generation will be imposed.
    :return: The next generation of the population.
    """
    start_time = time.time()
    # Select parents from the original population.
    parents = selection(individuals)

    # Crossover parents and add to the new population.
    cross_pop = crossover(parents)

    # Mutate the new population.
    new_pop = mutation(cross_pop)
    end_time = time.time()
    mut_time = end_time - start_time

    # Evaluate the fitness of the new population.
    new_pop, time_slot = evaluate_fitness(new_pop)
    time_slot = time_slot + mut_time

    start_time = time.time()
    # Replace the old population with the new population.
    individuals = replacement(new_pop, individuals)
    end_time = time.time()
    replacement_time = end_time - start_time
    time_slot = time_slot + replacement_time
    trackers.train_time_list.append(time_slot)

    # Generate statistics for run so far
    get_stats(individuals)

    return individuals


def steady_state_step(individuals):
    """
    Runs a single generation of the evolutionary algorithm process,
    using steady state replacement.

    :param individuals: The current generation, upon which a single
    evolutionary generation will be imposed.
    :return: The next generation of the population.
    """

    individuals = steady_state(individuals)

    return individuals
