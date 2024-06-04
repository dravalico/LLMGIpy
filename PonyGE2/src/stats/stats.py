from copy import copy
from sys import stdout
from time import time
import editdistance
import statistics
from collections.abc import Callable
import math
import numpy as np
from fitness.progimpr import progimpr
from algorithm.parameters import params
from utilities.algorithm.NSGA2 import compute_pareto_metrics
from utilities.algorithm.state import create_state
from utilities.stats import trackers
from utilities.stats.file_io import save_best_ind_to_file, \
    save_first_front_to_file, save_stats_headers, save_stats_to_file
from utilities.stats.save_plots import save_pareto_fitness_plot, \
    save_plot_from_data

"""Algorithm statistics"""
stats = {
    "gen": 0,
    "total_inds": 0,
    "regens": 0,
    "invalids": 0,
    "runtime_error": 0,
    "unique_inds": len(trackers.cache),
    "unused_search": 0,
    "ave_genome_length": 0,
    "max_genome_length": 0,
    "min_genome_length": 0,
    "med_genome_length": 0,
    "std_genome_length": 0,
    "q1_genome_length": 0,
    "q3_genome_length": 0,
    "ave_editdist": 0,
    "max_editdist": 0,
    "min_editdist": 0,
    "med_editdist": 0,
    "std_editdist": 0,
    "q1_editdist": 0,
    "q3_editdist": 0,
    "ave_used_codons": 0,
    "max_used_codons": 0,
    "min_used_codons": 0,
    "med_used_codons": 0,
    "std_used_codons": 0,
    "q1_used_codons": 0,
    "q3_used_codons": 0,
    "ave_tree_depth": 0,
    "max_tree_depth": 0,
    "min_tree_depth": 0,
    "med_tree_depth": 0,
    "std_tree_depth": 0,
    "q1_tree_depth": 0,
    "q3_tree_depth": 0,
    "ave_tree_nodes": 0,
    "max_tree_nodes": 0,
    "min_tree_nodes": 0,
    "med_tree_nodes": 0,
    "std_tree_nodes": 0,
    "q1_tree_nodes": 0,
    "q3_tree_nodes": 0,
    "ave_fitness": 0,
    "max_fitness": 0,
    "min_fitness": 0,
    "med_fitness": 0,
    "std_fitness": 0,
    "q1_fitness": 0,
    "q3_fitness": 0,
    "ave_test_fitness": 0,
    "max_test_fitness": 0,
    "min_test_fitness": 0,
    "med_test_fitness": 0,
    "std_test_fitness": 0,
    "q1_test_fitness": 0,
    "q3_test_fitness": 0,    
    "best_fitness": 0,
    "test_fitness_of_the_best": 0,
    "time_taken": 0,
    "total_time": 0,
    "time_adjust": 0
}


def compute_stats_all_distinct_distances(vectors: list, distance_function: Callable) -> dict[str, float]:
    distances: list[float] = []

    for i in range(len(vectors) - 1):
        for j in range(i + 1, len(vectors)):
            distances.append(distance_function(vectors[i], vectors[j]))

    return compute_some_stats(distances)


def compute_some_stats(distances: list[float]) -> dict[str, float]:
    stats: dict[str, float] = {}

    stats['ave'] = statistics.mean(distances)
    stats['med'] = statistics.median(distances)
    stats['max'] = max(distances)
    stats['min'] = min(distances)
    stats['std'] = statistics.pstdev(distances, mu=stats['ave'])
    stats['q1'] = float(np.percentile(distances, 25))
    stats['q3'] = float(np.percentile(distances, 75))

    return stats


def get_stats(individuals, end=False):
    """
    Generate the statistics for an evolutionary run. Save statistics to
    utilities.trackers.stats_list. Print statistics. Save fitness plot
    information.

    :param individuals: A population of individuals for which to generate
    statistics.
    :param end: Boolean flag for indicating the end of an evolutionary run.
    :return: Nothing.
    """

    if hasattr(params['FITNESS_FUNCTION'], 'multi_objective'):
        # Multiple objective optimisation is being used.

        # Remove fitness stats from the stats dictionary.
        stats.pop('test_fitness_of_the_best', None)
        for stats_key in stats.keys():
            if stats_key.endswith('fitness'):
                stats.pop(stats_key, None)

        # Update stats.
        get_moo_stats(individuals, end)

    else:
        # Single objective optimisation is being used.
        get_soo_stats(individuals, end)

    if params['SAVE_STATE'] and not params['DEBUG'] and \
            stats['gen'] % params['SAVE_STATE_STEP'] == 0:
        # Save the state of the current evolutionary run.
        create_state(individuals)


def get_soo_stats(individuals, end):
    """
    Generate the statistics for an evolutionary run with a single objective.
    Save statistics to utilities.trackers.stats_list. Print statistics. Save
    fitness plot information.

    :param individuals: A population of individuals for which to generate
    statistics.
    :param end: Boolean flag for indicating the end of an evolutionary run.
    :return: Nothing.
    """

    # Get best individual.
    best = max(individuals)
    test_fitness_of_the_best = best.levi_test_fitness

    if not trackers.best_ever or best > trackers.best_ever:
        # Save best individual in trackers.best_ever.
        trackers.best_ever = best

    if end or params['VERBOSE'] or not params['DEBUG']:
        # Update all stats.
        update_stats(individuals, end)

    # Save fitness plot information
    if params['SAVE_PLOTS'] and not params['DEBUG']:
        if not end:
            trackers.best_fitness_list.append(trackers.best_ever.fitness)
            trackers.test_fitness_of_the_best_list.append(trackers.best_ever.levi_test_fitness)

        if params['VERBOSE'] or end:
            save_plot_from_data(trackers.best_fitness_list, "best_fitness")
            save_plot_from_data(trackers.test_fitness_of_the_best_list, "test_fitness_of_the_best")

    # Print statistics
    if params['VERBOSE'] and not end:
        print_generation_stats()

    elif not params['SILENT']:
        # Print simple display output.
        perc = stats['gen'] / (params['GENERATIONS'] + 1) * 100
        stdout.write("Evolution: %d%% complete\r" % perc)
        stdout.flush()

    # Generate test fitness on regression problems
    if hasattr(params['FITNESS_FUNCTION'], "training_test") and end:
        # Save training fitness.
        trackers.best_ever.training_fitness = copy(trackers.best_ever.fitness)

        # Evaluate test fitness.
        trackers.best_ever.test_fitness = params['FITNESS_FUNCTION'](
            trackers.best_ever, dist='test')

        # Set main fitness as training fitness.
        trackers.best_ever.fitness = trackers.best_ever.training_fitness

        if params['FITNESS_FUNCTION'].__class__.__name__ == 'progimpr':
            temp_fitness_file = params['FITNESS_FILE']
            temp_ind_fitness = trackers.best_ever.fitness
            temp_ind_levi_test_fitness = trackers.best_ever.levi_test_fitness
            temp_ind_levi_errors = trackers.best_ever.levi_errors
            
            params['FITNESS_FILE'] = 'fitness_cases.txt'
            temp_fitness_class_instance = progimpr()
            rubber_train = temp_fitness_class_instance(trackers.best_ever, dist='training')
            rubber_test = temp_fitness_class_instance(trackers.best_ever, dist='test')
            trackers.best_ever.num_not_passed_cases_train = rubber_train
            trackers.best_ever.num_not_passed_cases_test = rubber_test

            params['FITNESS_FILE'] = temp_fitness_file
            trackers.best_ever.fitness = temp_ind_fitness
            trackers.best_ever.levi_test_fitness = temp_ind_levi_test_fitness
            trackers.best_ever.levi_errors = temp_ind_levi_errors

    # Save stats to list.
    if params['VERBOSE'] or (not params['DEBUG'] and not end):
        trackers.stats_list.append(copy(stats))

    # Save stats to file.
    if not params['DEBUG']:

        if stats['gen'] == 0:
            save_stats_headers(stats)

        save_stats_to_file(stats, end)

        if params['SAVE_ALL']:
            save_best_ind_to_file(stats, trackers.best_ever, end, stats['gen'])

        elif params['VERBOSE'] or end:
            save_best_ind_to_file(stats, trackers.best_ever, end)

    if end and not params['SILENT']:
        print_final_stats()


def get_moo_stats(individuals, end):
    """
    Generate the statistics for an evolutionary run with multiple objectives.
    Save statistics to utilities.trackers.stats_list. Print statistics. Save
    fitness plot information.

    :param individuals: A population of individuals for which to generate
    statistics.
    :param end: Boolean flag for indicating the end of an evolutionary run.
    :return: Nothing.
    """

    # Compute the pareto front metrics for the population.
    pareto = compute_pareto_metrics(individuals)

    # Save first front in trackers. Sort arbitrarily along first objective.
    trackers.best_ever = sorted(pareto.fronts[0], key=lambda x: x.fitness[0])

    # Store stats about pareto fronts.
    stats['pareto_fronts'] = len(pareto.fronts)
    stats['first_front'] = len(pareto.fronts[0])

    if end or params['VERBOSE'] or not params['DEBUG']:
        # Update all stats.
        update_stats(individuals, end)

    # Save fitness plot information
    if params['SAVE_PLOTS'] and not params['DEBUG']:

        # Initialise empty array for fitnesses for all inds on first pareto
        # front.
        all_arr = [[] for _ in range(params['FITNESS_FUNCTION'].num_obj)]

        # Generate array of fitness values.
        fitness_array = [ind.fitness for ind in trackers.best_ever]

        # Add paired fitnesses to array for graphing.
        for fit in fitness_array:
            for o in range(params['FITNESS_FUNCTION'].num_obj):
                all_arr[o].append(fit[o])

        if not end:
            trackers.first_pareto_list.append(all_arr)

            # Append empty array to best fitness list.
            trackers.best_fitness_list.append([])

            # Get best fitness for each objective.
            for o, ff in \
                    enumerate(params['FITNESS_FUNCTION'].fitness_functions):
                # Get sorted list of all fitness values for objective "o"
                fits = sorted(all_arr[o], reverse=ff.maximise)

                # Append best fitness to trackers list.
                trackers.best_fitness_list[-1].append(fits[0])

        if params['VERBOSE'] or end:

            # Plot best fitness for each objective.
            for o, ff in \
                    enumerate(params['FITNESS_FUNCTION'].fitness_functions):
                to_plot = [i[o] for i in trackers.best_fitness_list]

                # Plot fitness data for objective o.
                plotname = ff.__class__.__name__ + str(o)

                save_plot_from_data(to_plot, plotname)

            # TODO: PonyGE2 can currently only plot moo problems with 2
            #  objectives.
            # Check that the number of fitness objectives is not greater than 2
            if params['FITNESS_FUNCTION'].num_obj > 2:
                s = "stats.stats.get_moo_stats\n" \
                    "Warning: Plotting of more than 2 simultaneous " \
                    "objectives is not yet enabled in PonyGE2."
                print(s)

            else:
                save_pareto_fitness_plot()

    # Print statistics
    if params['VERBOSE'] and not end:
        print_generation_stats()
        print_first_front_stats()

    elif not params['SILENT']:
        # Print simple display output.
        perc = stats['gen'] / (params['GENERATIONS'] + 1) * 100
        stdout.write("Evolution: %d%% complete\r" % perc)
        stdout.flush()

    # Generate test fitness on regression problems
    if hasattr(params['FITNESS_FUNCTION'], "training_test") and end:

        for ind in trackers.best_ever:
            # Iterate over all individuals in the first front.

            # Save training fitness.
            ind.training_fitness = copy(ind.fitness)

            # Evaluate test fitness.
            ind.test_fitness = params['FITNESS_FUNCTION'](ind, dist='test')

            # Set main fitness as training fitness.
            ind.fitness = ind.training_fitness

    # Save stats to list.
    if params['VERBOSE'] or (not params['DEBUG'] and not end):
        trackers.stats_list.append(copy(stats))

    # Save stats to file.
    if not params['DEBUG']:

        if stats['gen'] == 0:
            save_stats_headers(stats)

        save_stats_to_file(stats, end)

        if params['SAVE_ALL']:
            save_first_front_to_file(stats, end, stats['gen'])

        elif params['VERBOSE'] or end:
            save_first_front_to_file(stats, end)

    if end and not params['SILENT']:
        print_final_moo_stats()


def update_stats(individuals, end):
    """
    Update all stats in the stats dictionary.

    :param individuals: A population of individuals.
    :param end: Boolean flag for indicating the end of an evolutionary run.
    :return: Nothing.
    """

    if not end:
        # Time Stats
        trackers.time_list.append(time() - stats['time_adjust'])
        stats['time_taken'] = trackers.time_list[-1] - \
                              trackers.time_list[-2]
        stats['total_time'] = trackers.time_list[-1] - \
                              trackers.time_list[0]

    # Population Stats
    stats['total_inds'] = params['POPULATION_SIZE'] * (stats['gen'] + 1)
    stats['runtime_error'] = len(trackers.runtime_error_cache)
    if params['CACHE']:
        stats['unique_inds'] = len(trackers.cache)
        stats['unused_search'] = 100 - stats['unique_inds'] / \
                                 stats['total_inds'] * 100

    # EditDistance-based diversity measure
    all_genomes = [i.genome for i in individuals]
    diversity_stats = compute_stats_all_distinct_distances(all_genomes, editdistance.eval)
    for diversity_stats_key in diversity_stats:
        stats[diversity_stats_key + '_' + 'editdist'] = diversity_stats[diversity_stats_key]
    
    # Genome Stats
    genome_lengths = [len(i.genome) for i in individuals]
    stats['max_genome_length'] = np.nanmax(genome_lengths)
    stats['ave_genome_length'] = np.nanmean(genome_lengths)
    stats['min_genome_length'] = np.nanmin(genome_lengths)
    stats['med_genome_length'] = np.nanmedian(genome_lengths)
    stats['std_genome_length'] = np.nanstd(genome_lengths)
    stats['q1_genome_length'] = np.nanpercentile(genome_lengths, 25)
    stats['q3_genome_length'] = np.nanpercentile(genome_lengths, 75)

    # Used Codon Stats
    codons = [i.used_codons for i in individuals]
    stats['max_used_codons'] = np.nanmax(codons)
    stats['ave_used_codons'] = np.nanmean(codons)
    stats['min_used_codons'] = np.nanmin(codons)
    stats['med_used_codons'] = np.nanmedian(codons)
    stats['std_used_codons'] = np.nanstd(codons)
    stats['q1_used_codons'] = np.nanpercentile(codons, 25)
    stats['q3_used_codons'] = np.nanpercentile(codons, 75)

    # Tree Depth Stats
    depths = [i.depth for i in individuals]
    stats['max_tree_depth'] = np.nanmax(depths)
    stats['ave_tree_depth'] = np.nanmean(depths)
    stats['min_tree_depth'] = np.nanmin(depths)
    stats['med_tree_depth'] = np.nanmedian(depths)
    stats['std_tree_depth'] = np.nanstd(depths)
    stats['q1_tree_depth'] = np.nanpercentile(depths, 25)
    stats['q3_tree_depth'] = np.nanpercentile(depths, 75)

    # Tree Node Stats
    nodes = [i.nodes for i in individuals]
    stats['max_tree_nodes'] = np.nanmax(nodes)
    stats['ave_tree_nodes'] = np.nanmean(nodes)
    stats['min_tree_nodes'] = np.nanmin(nodes)
    stats['med_tree_nodes'] = np.nanmedian(nodes)
    stats['std_tree_nodes'] = np.nanstd(nodes)
    stats['q1_tree_nodes'] = np.nanpercentile(nodes, 25)
    stats['q3_tree_nodes'] = np.nanpercentile(nodes, 75)

    if not hasattr(params['FITNESS_FUNCTION'], 'multi_objective'):
        # Fitness Stats
        fitnesses = [i.fitness for i in individuals if not math.isnan(i.fitness) and i.fitness < 9223372036854775807]
        all_test_fitnesses = [i.levi_test_fitness for i in individuals if not math.isnan(i.levi_test_fitness) and i.levi_test_fitness < 9223372036854775807]
        if (len(fitnesses) != 0):
            stats['max_fitness'] = np.nanmax(fitnesses)
            stats['ave_fitness'] = np.nanmean(fitnesses)
            stats['min_fitness'] = np.nanmin(fitnesses)
            stats['med_fitness'] = np.nanmedian(fitnesses)
            stats['std_fitness'] = np.nanstd(fitnesses)
            stats['q1_fitness'] = np.nanpercentile(fitnesses, 25)
            stats['q3_fitness'] = np.nanpercentile(fitnesses, 75)
        else:
            stats['max_fitness'] = 0.0
            stats['ave_fitness'] = 0.0
            stats['min_fitness'] = 0.0
            stats['med_fitness'] = 0.0
            stats['std_fitness'] = 0.0
            stats['q1_fitness'] = 0.0
            stats['q3_fitness'] = 0.0

        if (len(all_test_fitnesses) != 0):
            stats['max_test_fitness'] = np.nanmax(all_test_fitnesses)
            stats['ave_test_fitness'] = np.nanmean(all_test_fitnesses)
            stats['min_test_fitness'] = np.nanmin(all_test_fitnesses)
            stats['med_test_fitness'] = np.nanmedian(all_test_fitnesses)
            stats['std_test_fitness'] = np.nanstd(all_test_fitnesses)
            stats['q1_test_fitness'] = np.nanpercentile(all_test_fitnesses, 25)
            stats['q3_test_fitness'] = np.nanpercentile(all_test_fitnesses, 75)
        else:
            stats['max_test_fitness'] = 0.0
            stats['ave_test_fitness'] = 0.0
            stats['min_test_fitness'] = 0.0
            stats['med_test_fitness'] = 0.0
            stats['std_test_fitness'] = 0.0
            stats['q1_test_fitness'] = 0.0
            stats['q3_test_fitness'] = 0.0
        
        stats['best_fitness'] = trackers.best_ever.fitness
        stats['test_fitness_of_the_best'] = trackers.best_ever.levi_test_fitness


def print_generation_stats():
    """
    Print the statistics for the generation and individuals.

    :return: Nothing.
    """

    print("______\n")
    for stat in sorted(stats.keys()):
        if not (stat.startswith('ave_') or stat.startswith('q1_') or stat.startswith('q3_')):
            print(" ", stat, ": \t", stats[stat])
    print("\n")


def print_first_front_stats():
    """
    Stats printing for the first pareto front for multi-objective optimisation.

    :return: Nothing.
    """

    print("  first front fitnesses :")
    for ind in trackers.best_ever:
        print("\t  ", ind.fitness)


def print_final_stats():
    """
    Prints a final review of the overall evolutionary process.

    :return: Nothing.
    """

    if hasattr(params['FITNESS_FUNCTION'], "training_test"):
        print("\n\nBest:\n  Training fitness:\t",
              trackers.best_ever.training_fitness)
        print("  Test fitness:\t\t", trackers.best_ever.test_fitness)
        if params['FITNESS_FUNCTION'].__class__.__name__ == 'progimpr':
            print("  Train num not passed cases:\t\t", trackers.best_ever.num_not_passed_cases_train)
            print("  Test num not passed cases:\t\t", trackers.best_ever.num_not_passed_cases_test)
    else:
        print("\n\nBest:\n  Fitness:\t", trackers.best_ever.fitness)

    print("  Phenotype:", trackers.best_ever.phenotype)
    print("  Genome:", trackers.best_ever.genome)
    print_generation_stats()


def print_final_moo_stats():
    """
    Prints a final review of the overall evolutionary process for
    multi-objective problems.

    :return: Nothing.
    """

    print("\n\nFirst Front:")
    for ind in trackers.best_ever:
        print(" ", ind)
    print_generation_stats()
