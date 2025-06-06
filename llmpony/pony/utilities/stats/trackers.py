"""Utilities for tracking progress of runs, including time taken per
generation, fitness plots, fitness caches, etc."""

cache = {}
# This dict stores the cache for an evolutionary run. The key for each entry
# is the phenotype of the individual, the value is its fitness.

cache_test_set = {}
# This dict stores the cache for an evolutionary run. The key for each entry
# is the phenotype of the individual, the value is its fitness on the test set.

cache_levi_errors = {}
# This dict stores the cache for an evolutionary run. The key for each entry
# is the phenotype of the individual, the value is its errors on the training set.

runtime_error_cache = []
# This list stores a list of phenotypes which produce runtime errors over an
# evolutionary run.

best_fitness_list = []
# fitness_plot is simply a list of the best fitnesses at each generation.
# Useful for plotting evolutionary progress.

test_fitness_of_the_best_list = []
# fitness_plot is simply a list of the test fitnesses of the best for each generation.
# Useful for plotting evolutionary progress.

first_pareto_list = []
# first_pareto_list stores the list of all individuals stored on the first
# pareto front during multi objective optimisation.

time_list = []
# time_list stores the system time after each generation has been completed.
# Useful for keeping track of how long each generation takes.

train_time_list = []
# train_time_list stores the system time after each generation has been completed.
# Useful for keeping track of how long each generation takes.
# Only accounts for the fitness evaluations on the training set for each generation and ignores computation of additional statistics.

stats_list = []
# List for storing stats at each generation
# Used when verbose mode is off to speed up program

best_ever = None
# Store the best ever individual here.

best_individuals_ever = []
# Store all the best individuals ever for each generation