#!/usr/bin/env python
"""
@author: Jonathan Byrne
@17/01/18 11:09
"""

import numpy as np
from fitness.base_ff_classes.base_ff import base_ff


class singlefit_multiobj(base_ff):
    """
    An example of a single fitness class that generates
    two fitness values for multi-objective optimisation
    """

    maximise = True
    multi_objective = True

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()

        # Set list of individual fitness functions.
        self.num_obj = 2
        dummyfit = base_ff()
        dummyfit.maximise = True
        self.fitness_functions = [dummyfit, dummyfit]
        self.default_fitness = [float('nan'), float('nan')]

    def evaluate(self, ind, **kwargs):
        """Dummy fitness function that generates 2 fitness values"""
        phenotype = ind.phenotype
        fitness = 0
        settings = {}

        # try:
        #     exec(phenotype, settings)
        # except Exception as e:
        #     fitness = self.default_fitness
        #     print("Error", e)

        # Using dummy fitness values for the moment.
        x = np.random.pareto(4, 2)
        fitness = [x[0], x[1]]

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
