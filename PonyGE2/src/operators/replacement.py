from algorithm.parameters import params
from fitness.evaluation import evaluate_fitness
from operators.crossover import crossover_inds
from operators.mutation import mutation
from operators.selection import selection
from utilities.algorithm.NSGA2 import compute_pareto_metrics


def replacement(new_pop, old_pop):
    """
    Given a new population and an old population, performs replacement using
    specified replacement operator.
    
    :param new_pop: Newly generated population (after selection, variation &
    evaluation).
    :param old_pop: The previous generation population.
    :return: Replaced population.
    """
    return params['REPLACEMENT'](new_pop, old_pop)


def generational(new_pop, old_pop):
    """
    Replaces the old population with the new population. The ELITE_SIZE best
    individuals from the previous population are appended to new pop regardless
    of whether or not they are better than the worst individuals in new pop.
    
    :param new_pop: The new population (e.g. after selection, variation, &
    evaluation).
    :param old_pop: The previous generation population, from which elites
    are taken.
    :return: The 'POPULATION_SIZE' new population with elites.
    """

    # Sort both populations.
    old_pop.sort(reverse=True)
    new_pop.sort(reverse=True)

    # Append the best ELITE_SIZE individuals from the old population to the
    # new population.
    for ind in old_pop[:params['ELITE_SIZE']]:
        new_pop.insert(0, ind)

    # Return the top POPULATION_SIZE individuals of the new pop, including
    # elites.
    return new_pop[:params['POPULATION_SIZE']]


def steady_state(individuals):
    """
    Runs a single generation of the evolutionary algorithm process,
    using steady state replacement:
        Selection
        Variation
        Evaluation
        Replacement
        
    Steady state replacement uses the Genitor model (Whitley, 1989) whereby
    new individuals directly replace the worst individuals in the population
    regardless of whether or not the new individuals are fitter than those
    they replace. Note that traditional GP crossover generates only 1 child,
    whereas linear GE crossover (and thus all crossover functions used in
    PonyGE) generates 2 children from 2 parents. Thus, we use a deletion
    strategy of 2.

    :param individuals: The current generation, upon which a single
    evolutionary generation will be imposed.
    :return: The next generation of the population.
    """

    # Initialise counter for new individuals.
    ind_counter = 0

    while ind_counter < params['POPULATION_SIZE']:

        # Select parents from the original population.
        parents = selection(individuals)

        # Perform crossover on selected parents.
        cross_pop = crossover_inds(parents[0], parents[1])

        if cross_pop is None:
            # Crossover failed.
            pass

        else:
            # Mutate the new population.
            new_pop = mutation(cross_pop)

            # Evaluate the fitness of the new population.
            new_pop = evaluate_fitness(new_pop)

            # Sort the original population
            individuals.sort(reverse=True)

            # Combine both populations
            total_pop = individuals[:-len(new_pop)] + new_pop

            # Increment the ind counter
            ind_counter += params['GENERATION_SIZE']

    # Return the combined population.
    return total_pop


def nsga2_replacement(new_pop, old_pop):
    """
    Replaces the old population with the new population using NSGA-II
    replacement. Both new and old populations are combined, pareto fronts
    and crowding distance are calculated, and the replacement population is
    computed based on crowding distance per pareto front.
    
    :param new_pop: The new population (e.g. after selection, variation, &
                    evaluation).
    :param old_pop: The previous generation population.
    :return: The 'POPULATION_SIZE' new population.
    """

    # Combine both populations (R_t = P_t union Q_t)
    new_pop.extend(old_pop)

    # Compute the pareto fronts and crowding distance
    pareto = compute_pareto_metrics(new_pop)

    # Size of the new population
    pop_size = params['POPULATION_SIZE']

    # New population to replace the last one
    temp_pop, i = [], 0

    while len(temp_pop) < pop_size:
        # Populate the replacement population

        if len(pareto.fronts[i]) <= pop_size - len(temp_pop):
            temp_pop.extend(pareto.fronts[i])

        else:
            # Sort the current pareto front with respect to crowding distance.
            pareto.fronts[i] = sorted(pareto.fronts[i],
                                      key=lambda item:
                                      pareto.crowding_distance[item],
                                      reverse=True)

            # Get number of individuals to add in temp to achieve the pop_size
            diff_size = pop_size - len(temp_pop)

            # Extend the replacement population
            temp_pop.extend(pareto.fronts[i][:diff_size])

        # Increment counter.
        i += 1

    return temp_pop


# Set attributes for all operators to define multi-objective operators.
nsga2_replacement.multi_objective = True
