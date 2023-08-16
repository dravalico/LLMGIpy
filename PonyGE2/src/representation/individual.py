import numpy as np

from algorithm.mapper import mapper
from algorithm.parameters import params


class Individual(object):
    """
    A GE individual.
    """

    def __init__(self, genome, ind_tree, map_ind=True):
        """
        Initialise an instance of the individual class (i.e. create a new
        individual).

        :param genome: An individual's genome.
        :param ind_tree: An individual's derivation tree, i.e. an instance
        of the representation.tree.Tree class.
        :param map_ind: A boolean flag that indicates whether or not an
        individual needs to be mapped.
        """

        if map_ind:
            # The individual needs to be mapped from the given input
            # parameters.
            self.phenotype, self.genome, self.tree, self.nodes, self.invalid, \
            self.depth, self.used_codons = mapper(genome, ind_tree)

        else:
            # The individual does not need to be mapped.
            self.genome, self.tree = genome, ind_tree

        self.fitness = params['FITNESS_FUNCTION'].default_fitness
        self.runtime_error = False
        self.name = None

    def __lt__(self, other):
        """
        Set the definition for comparison of two instances of the individual
        class by their fitness values. Allows for sorting/ordering of a
        population of individuals. Note that numpy NaN is used for invalid
        individuals and is used by some fitness functions as a default fitness.
        We implement a custom catch for these NaN values.

        :param other: Another instance of the individual class (i.e. another
        individual) with which to compare.
        :return: Whether or not the fitness of the current individual is
        greater than the comparison individual.
        """

        if np.isnan(self.fitness):
            return True
        elif np.isnan(other.fitness):
            return False
        else:
            return self.fitness < other.fitness if params[
                'FITNESS_FUNCTION'].maximise else other.fitness < self.fitness

    def __le__(self, other):
        """
        Set the definition for comparison of two instances of the individual
        class by their fitness values. Allows for sorting/ordering of a
        population of individuals. Note that numpy NaN is used for invalid
        individuals and is used by some fitness functions as a default fitness.
        We implement a custom catch for these NaN values.

        :param other: Another instance of the individual class (i.e. another
        individual) with which to compare.
        :return: Whether or not the fitness of the current individual is
        greater than or equal to the comparison individual.
        """

        if np.isnan(self.fitness):
            return True
        elif np.isnan(other.fitness):
            return False
        else:
            return self.fitness <= other.fitness if params[
                'FITNESS_FUNCTION'].maximise else other.fitness <= self.fitness

    def __str__(self):
        """
        Generates a string by which individuals can be identified. Useful
        for printing information about individuals.

        :return: A string describing the individual.
        """
        return ("Individual: " +
                str(self.phenotype) + "; " + str(self.fitness))

    def deep_copy(self):
        """
        Copy an individual and return a unique version of that individual.

        :return: A unique copy of the individual.
        """

        if not params['GENOME_OPERATIONS']:
            # Create a new unique copy of the tree.
            new_tree = self.tree.__copy__()

        else:
            new_tree = None

        # Create a copy of self by initialising a new individual.
        new_ind = Individual(self.genome.copy(), new_tree, map_ind=False)

        # Set new individual parameters (no need to map genome to new
        # individual).
        new_ind.phenotype, new_ind.invalid = self.phenotype, self.invalid
        new_ind.depth, new_ind.nodes = self.depth, self.nodes
        new_ind.used_codons = self.used_codons
        new_ind.runtime_error = self.runtime_error

        return new_ind

    def evaluate(self):
        """
        Evaluates phenotype in using the fitness function set in the params
        dictionary. For regression/classification problems, allows for
        evaluation on either training or test distributions. Sets fitness
        value.

        :return: Nothing unless multi-core evaluation is being used. In that
        case, returns self.
        """

        # Evaluate fitness using specified fitness function.
        self.fitness = params['FITNESS_FUNCTION'](self)

        if params['MULTICORE']:
            return self
