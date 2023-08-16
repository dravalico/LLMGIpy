from fitness.evaluation import evaluate_fitness
from operators.crossover import crossover
from operators.mutation import mutation
from operators.replacement import replacement, steady_state
from operators.selection import selection
from stats.stats import get_stats


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

    # Select parents from the original population.
    parents = selection(individuals)

    # Crossover parents and add to the new population.
    cross_pop = crossover(parents)

    # Mutate the new population.
    new_pop = mutation(cross_pop)

    # Evaluate the fitness of the new population.
    new_pop = evaluate_fitness(new_pop)

    # Replace the old population with the new population.
    individuals = replacement(new_pop, individuals)

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
