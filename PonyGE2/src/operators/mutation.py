from random import choice, randint, random

from algorithm.parameters import params
from representation import individual
from representation.derivation import generate_tree
from representation.latent_tree import latent_tree_mutate, latent_tree_repair
from utilities.representation.check_methods import check_ind


def mutation(pop):
    """
    Perform mutation on a population of individuals. Calls mutation operator as
    specified in params dictionary.

    :param pop: A population of individuals to be mutated.
    :return: A fully mutated population.
    """

    # Initialise empty pop for mutated individuals.
    new_pop = []

    # Iterate over entire population.
    for ind in pop:

        # If individual has no genome, default to subtree mutation.
        if not ind.genome and params['NO_MUTATION_INVALIDS']:
            new_ind = subtree(ind)

        else:
            # Perform mutation.
            new_ind = params['MUTATION'](ind)

        # Check ind does not violate specified limits.
        check = check_ind(new_ind, "mutation")

        while check:
            # Perform mutation until the individual passes all tests.

            # If individual has no genome, default to subtree mutation.
            if not ind.genome and params['NO_MUTATION_INVALIDS']:
                new_ind = subtree(ind)

            else:
                # Perform mutation.
                new_ind = params['MUTATION'](ind)

            # Check ind does not violate specified limits.
            check = check_ind(new_ind, "mutation")

        # Append mutated individual to population.
        new_pop.append(new_ind)

    return new_pop


def int_flip_per_codon(ind):
    """
    Mutate the genome of an individual by randomly choosing a new int with
    probability p_mut. Works per-codon. Mutation is performed over the
    effective length (i.e. within used codons, not tails) by default;
    within_used=False switches this off.

    :param ind: An individual to be mutated.
    :return: A mutated individual.
    """

    # Set effective genome length over which mutation will be performed.
    eff_length = get_effective_length(ind)

    if not eff_length:
        # Linear mutation cannot be performed on this individual.
        return ind

    # Set mutation probability. 
    if params['MUTATION_PROBABILITY'] is not None:
        p_mut = params['MUTATION_PROBABILITY']
    else:
        # Default is 1 divided by genome length.
        p_mut = 1.0 / eff_length

    # Mutation probability works per-codon over the portion of the
    # genome as defined by the within_used flag.
    for i in range(eff_length):
        if random() < p_mut:
            ind.genome[i] = randint(0, params['CODON_SIZE'])

    # Re-build a new individual with the newly mutated genetic information.
    new_ind = individual.Individual(ind.genome, None)

    return new_ind


def int_flip_per_ind(ind):
    """
    Mutate the genome of an individual by randomly choosing a new int with
    probability p_mut. Works per-individual. Mutation is performed over the
    entire length of the genome by default, but the flag within_used is
    provided to limit mutation to only the effective length of the genome.

    :param ind: An individual to be mutated.
    :return: A mutated individual.
    """

    # Set effective genome length over which mutation will be performed.
    eff_length = get_effective_length(ind)

    if not eff_length:
        # Linear mutation cannot be performed on this individual.
        return ind

    for _ in range(params['MUTATION_EVENTS']):
        idx = randint(0, eff_length - 1)
        ind.genome[idx] = randint(0, params['CODON_SIZE'])

    # Re-build a new individual with the newly mutated genetic information.
    new_ind = individual.Individual(ind.genome, None)

    return new_ind


def subtree(ind):
    """
    Mutate the individual by replacing a randomly selected subtree with a
    new randomly generated subtree. Guaranteed one event per individual, unless
    params['MUTATION_EVENTS'] is specified as a higher number.

    :param ind: An individual to be mutated.
    :return: A mutated individual.
    """

    def subtree_mutate(ind_tree):
        """
        Creates a list of all nodes and picks one node at random to mutate.
        Because we have a list of all nodes, we can (but currently don't)
        choose what kind of nodes to mutate on. Handy.

        :param ind_tree: The full tree of an individual.
        :return: The full mutated tree and the associated genome.
        """

        # Find the list of nodes we can mutate from.
        targets = ind_tree.get_target_nodes([], target=params[
            'BNF_GRAMMAR'].non_terminals)

        # Pick a node.
        new_tree = choice(targets)

        # Set the depth limits for the new subtree.
        if params['MAX_TREE_DEPTH']:
            # Set the limit to the tree depth.
            max_depth = params['MAX_TREE_DEPTH'] - new_tree.depth

        else:
            # There is no limit to tree depth.
            max_depth = None

        # Mutate a new subtree.
        generate_tree(new_tree, [], [], "random", 0, 0, 0, max_depth)

        return ind_tree

    if ind.invalid:
        # The individual is invalid.
        tail = []

    else:
        # Save the tail of the genome.
        tail = ind.genome[ind.used_codons:]

    # Allows for multiple mutation events should that be desired.
    for i in range(params['MUTATION_EVENTS']):
        ind.tree = subtree_mutate(ind.tree)

    # Re-build a new individual with the newly mutated genetic information.
    ind = individual.Individual(None, ind.tree)

    # Add in the previous tail.
    ind.genome = ind.genome + tail

    return ind


def get_effective_length(ind):
    """
    Return the effective length of the genome for linear mutation.

    :param ind: An individual.
    :return: The effective length of the genome.
    """

    if not ind.genome:
        # The individual does not have a genome; linear mutation cannot be
        # performed.
        return None

    elif ind.invalid:
        # Individual is invalid.
        eff_length = len(ind.genome)

    elif params['WITHIN_USED']:
        eff_length = min(len(ind.genome), ind.used_codons)

    else:
        eff_length = len(ind.genome)

    return eff_length


def LTGE_mutation(ind):
    """Mutation in the LTGE representation."""

    # mutate and repair.
    g, ph = latent_tree_repair(latent_tree_mutate(ind.genome),
                               params['BNF_GRAMMAR'], params['MAX_TREE_DEPTH'])

    # wrap up in an Individual and fix up various Individual attributes
    ind = individual.Individual(g, None, False)

    ind.phenotype = ph

    # number of nodes is the number of decisions in the genome
    ind.nodes = ind.used_codons = len(g)

    # each key is the length of a path from root
    ind.depth = max(len(k) for k in g)

    # in LTGE there are no invalid individuals
    ind.invalid = False

    return ind


# Set attributes for all operators to define linear or subtree representations.
int_flip_per_codon.representation = "linear"
int_flip_per_ind.representation = "linear"
subtree.representation = "subtree"
LTGE_mutation.representation = "latent tree"
