from math import isnan

import numpy as np

np.seterr(all="raise")


class moo_ff:
    """
    Fitness function for multi-objective optimization problems. This fitness
    function acts as a holding class for all specified fitness functions.
    Individual fitness functions are held in an array called
    self.fitness_functions; when an individual is evaluated, it is evaluated
    on all fitness functions in this array.
    
    This is a holding class which exists just to be subclassed: it should not
    be instantiated.
    """

    # Required attribute for stats handling.
    multi_objective = True

    def __init__(self, fitness_functions):

        # Set list of individual fitness functions.
        self.fitness_functions = fitness_functions
        self.num_obj = len(fitness_functions)

        # Initialise individual fitness functions.
        for i, ff in enumerate(self.fitness_functions):
            self.fitness_functions[i] = ff()

        # Set up list of default fitness values (as per individual fitness
        # functions).
        self.default_fitness = []
        for f in fitness_functions:
            self.default_fitness.append(f.default_fitness)

    def __call__(self, ind):
        """
        Note that math functions used in the solutions are imported from either
        utilities.fitness.math_functions or called from numpy.
        
        :param ind: An individual to be evaluated.
        :return: The fitness of the evaluated individual.
        """

        # the multi-objective fitness is defined as a list of values, each one
        # representing the output of one objective function. The computation is
        # made by the function multi_objc_eval, implemented by a subclass,
        # according to the problem.
        fitness = [ff(ind) for ff in self.fitness_functions]

        if any([isnan(i) for i in fitness]):
            # Check if any objective fitness value is NaN, if so set default
            # fitness.
            fitness = self.default_fitness

        return fitness

    @staticmethod
    def value(fitness_vector, objective_index):
        """
        This is a static method required by NSGA-II for sorting populations
        based on a given fitness function, or for returning a given index of a
        population based on a given fitness function.
        
        :param fitness_vector: A vector/list of fitnesses.
        :param objective_index: The index of the desired fitness.
        :return: The fitness at the objective index of the fitness vector.
        """

        if not isinstance(fitness_vector, list):
            return float("inf")

        return fitness_vector[objective_index]
