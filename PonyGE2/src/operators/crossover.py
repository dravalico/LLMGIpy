from random import choice, randint, random, sample

from algorithm.parameters import params
from representation import individual
from representation.latent_tree import latent_tree_crossover, \
    latent_tree_repair
from utilities.representation.check_methods import check_ind


def crossover(parents):
    """
    Perform crossover on a population of individuals. The size of the crossover
    population is defined as params['GENERATION_SIZE'] rather than params[
    'POPULATION_SIZE']. This saves on wasted evaluations and prevents search
    from evaluating too many individuals.
    
    :param parents: A population of parent individuals on which crossover is to
    be performed.
    :return: A population of fully crossed over individuals.
    """

    # Initialise an empty population.
    cross_pop = []

    while len(cross_pop) < params['GENERATION_SIZE']:

        # Randomly choose two parents from the parent population.
        inds_in = sample(parents, 2)

        # Perform crossover on chosen parents.
        inds_out = crossover_inds(inds_in[0], inds_in[1])

        if inds_out is None:
            # Crossover failed.
            pass

        else:

            # Extend the new population.
            cross_pop.extend(inds_out)

    return cross_pop


def crossover_inds(parent_0, parent_1):
    """
    Perform crossover on two selected individuals.
    
    :param parent_0: Parent 0 selected for crossover.
    :param parent_1: Parent 1 selected for crossover.
    :return: Two crossed-over individuals.
    """

    # Create copies of the original parents. This is necessary as the
    # original parents remain in the parent population and changes will
    # affect the originals unless they are cloned.
    ind_0 = parent_0.deep_copy()
    ind_1 = parent_1.deep_copy()

    # Crossover cannot be performed on invalid individuals.
    if not params['INVALID_SELECTION'] and (ind_0.invalid or ind_1.invalid):
        s = "operators.crossover.crossover\nError: invalid individuals " \
            "selected for crossover."
        raise Exception(s)

    # Perform crossover on ind_0 and ind_1.
    inds = params['CROSSOVER'](ind_0, ind_1)

    # Check each individual is ok (i.e. does not violate specified limits).
    checks = [check_ind(ind, "crossover") for ind in inds]

    if any(checks):
        # An individual violates a limit.
        return None

    else:
        # Crossover was successful, return crossed-over individuals.
        return inds


def variable_onepoint(p_0, p_1):
    """
    Given two individuals, create two children using one-point crossover and
    return them. A different point is selected on each genome for crossover
    to occur. Note that this allows for genomes to grow or shrink in
    size. Crossover points are selected within the used portion of the
    genome by default (i.e. crossover does not occur in the tail of the
    individual).
    
    :param p_0: Parent 0
    :param p_1: Parent 1
    :return: A list of crossed-over individuals.
    """

    # Get the chromosomes.
    genome_0, genome_1 = p_0.genome, p_1.genome

    # Uniformly generate crossover points.
    max_p_0, max_p_1 = get_max_genome_index(p_0, p_1)

    # Select unique points on each genome for crossover to occur.
    pt_0, pt_1 = randint(1, max_p_0), randint(1, max_p_1)

    # Make new chromosomes by crossover: these slices perform copies.
    if random() < params['CROSSOVER_PROBABILITY']:
        c_0 = genome_0[:pt_0] + genome_1[pt_1:]
        c_1 = genome_1[:pt_1] + genome_0[pt_0:]
    else:
        c_0, c_1 = genome_0[:], genome_1[:]

    # Put the new chromosomes into new individuals.
    ind_0 = individual.Individual(c_0, None)
    ind_1 = individual.Individual(c_1, None)

    return [ind_0, ind_1]


def fixed_onepoint(p_0, p_1):
    """
    Given two individuals, create two children using one-point crossover and
    return them. The same point is selected on both genomes for crossover
    to occur. Crossover points are selected within the used portion of the
    genome by default (i.e. crossover does not occur in the tail of the
    individual).

    :param p_0: Parent 0
    :param p_1: Parent 1
    :return: A list of crossed-over individuals.
    """

    # Get the chromosomes.
    genome_0, genome_1 = p_0.genome, p_1.genome

    # Uniformly generate crossover points.
    max_p_0, max_p_1 = get_max_genome_index(p_0, p_1)

    # Select the same point on both genomes for crossover to occur.
    pt = randint(1, min(max_p_0, max_p_1))

    # Make new chromosomes by crossover: these slices perform copies.
    if random() < params['CROSSOVER_PROBABILITY']:
        c_0 = genome_0[:pt] + genome_1[pt:]
        c_1 = genome_1[:pt] + genome_0[pt:]
    else:
        c_0, c_1 = genome_0[:], genome_1[:]

    # Put the new chromosomes into new individuals.
    ind_0 = individual.Individual(c_0, None)
    ind_1 = individual.Individual(c_1, None)

    return [ind_0, ind_1]


def fixed_twopoint(p_0, p_1):
    """
    Given two individuals, create two children using two-point crossover and
    return them. The same points are selected on both genomes for crossover
    to occur. Crossover points are selected within the used portion of the
    genome by default (i.e. crossover does not occur in the tail of the
    individual).

    :param p_0: Parent 0
    :param p_1: Parent 1
    :return: A list of crossed-over individuals.
    """

    genome_0, genome_1 = p_0.genome, p_1.genome

    # Uniformly generate crossover points.
    max_p_0, max_p_1 = get_max_genome_index(p_0, p_1)

    # Select the same points on both genomes for crossover to occur.
    a, b = randint(1, max_p_0), randint(1, max_p_1)
    pt_0, pt_1 = min([a, b]), max([a, b])

    # Make new chromosomes by crossover: these slices perform copies.
    if random() < params['CROSSOVER_PROBABILITY']:
        c_0 = genome_0[:pt_0] + genome_1[pt_0:pt_1] + genome_0[pt_1:]
        c_1 = genome_1[:pt_0] + genome_0[pt_0:pt_1] + genome_1[pt_1:]
    else:
        c_0, c_1 = genome_0[:], genome_1[:]

    # Put the new chromosomes into new individuals.
    ind_0 = individual.Individual(c_0, None)
    ind_1 = individual.Individual(c_1, None)

    return [ind_0, ind_1]


def variable_twopoint(p_0, p_1):
    """
    Given two individuals, create two children using two-point crossover and
    return them. Different points are selected on both genomes for crossover
    to occur. Note that this allows for genomes to grow or shrink in size.
    Crossover points are selected within the used portion of the genome by
    default (i.e. crossover does not occur in the tail of the individual).

    :param p_0: Parent 0
    :param p_1: Parent 1
    :return: A list of crossed-over individuals.
    """

    genome_0, genome_1 = p_0.genome, p_1.genome

    # Uniformly generate crossover points.
    max_p_0, max_p_1 = get_max_genome_index(p_0, p_1)

    # Select the same points on both genomes for crossover to occur.
    a_0, b_0 = randint(1, max_p_0), randint(1, max_p_1)
    a_1, b_1 = randint(1, max_p_0), randint(1, max_p_1)
    pt_0, pt_1 = min([a_0, b_0]), max([a_0, b_0])
    pt_2, pt_3 = min([a_1, b_1]), max([a_1, b_1])

    # Make new chromosomes by crossover: these slices perform copies.
    if random() < params['CROSSOVER_PROBABILITY']:
        c_0 = genome_0[:pt_0] + genome_1[pt_2:pt_3] + genome_0[pt_1:]
        c_1 = genome_1[:pt_2] + genome_0[pt_0:pt_1] + genome_1[pt_3:]
    else:
        c_0, c_1 = genome_0[:], genome_1[:]

    # Put the new chromosomes into new individuals.
    ind_0 = individual.Individual(c_0, None)
    ind_1 = individual.Individual(c_1, None)

    return [ind_0, ind_1]


def subtree(p_0, p_1):
    """
    Given two individuals, create two children using subtree crossover and
    return them. Candidate subtrees are selected based on matching
    non-terminal nodes rather than matching terminal nodes.
    
    :param p_0: Parent 0.
    :param p_1: Parent 1.
    :return: A list of crossed-over individuals.
    """

    def do_crossover(tree0, tree1, shared_nodes):
        """
        Given two instances of the representation.tree.Tree class (
        derivation trees of individuals) and a list of intersecting
        non-terminal nodes across both trees, performs subtree crossover on
        these trees.
        
        :param tree0: The derivation tree of individual 0.
        :param tree1: The derivation tree of individual 1.
        :param shared_nodes: The sorted list of all non-terminal nodes that are
        in both derivation trees.
        :return: The new derivation trees after subtree crossover has been
        performed.
        """

        # Randomly choose a non-terminal from the set of permissible
        # intersecting non-terminals.
        crossover_choice = choice(shared_nodes)

        # Find all nodes in both trees that match the chosen crossover node.
        nodes_0 = tree0.get_target_nodes([], target=[crossover_choice])
        nodes_1 = tree1.get_target_nodes([], target=[crossover_choice])

        # Randomly pick a node.
        t0, t1 = choice(nodes_0), choice(nodes_1)

        # Check the parents of both chosen subtrees.
        p0 = t0.parent
        p1 = t1.parent

        if not p0 and not p1:
            # Crossover is between the entire tree of both tree0 and tree1.

            return t1, t0

        elif not p0:
            # Only t0 is the entire of tree0.
            tree0 = t1

            # Swap over the subtrees between parents.
            i1 = [id(i) for i in p1.children].index(id(t1))
            p1.children[i1] = t0

            # Set the parents of the crossed-over subtrees as their new
            # parents. Since the entire tree of t1 is now a whole
            # individual, it has no parent.
            t0.parent = p1
            t1.parent = None

        elif not p1:
            # Only t1 is the entire of tree1.
            tree1 = t0

            # Swap over the subtrees between parents.
            i0 = [id(i) for i in p0.children].index(id(t0))
            p0.children[i0] = t1

            # Set the parents of the crossed-over subtrees as their new
            # parents. Since the entire tree of t0 is now a whole
            # individual, it has no parent.
            t1.parent = p0
            t0.parent = None

        else:
            # The crossover node for both trees is not the entire tree.

            # For the parent nodes of the original subtrees, get the indexes
            # of the original subtrees.
            i0 = [id(i) for i in p0.children].index(id(t0))
            i1 = [id(i) for i in p1.children].index(id(t1))

            # Swap over the subtrees between parents.
            p0.children[i0] = t1
            p1.children[i1] = t0

            # Set the parents of the crossed-over subtrees as their new
            # parents.
            t1.parent = p0
            t0.parent = p1

        return tree0, tree1

    def intersect(l0, l1):
        """
        Returns the intersection of two sets of labels of nodes of
        derivation trees. Only returns matching non-terminal nodes across
        both derivation trees.
        
        :param l0: The labels of all nodes of tree 0.
        :param l1: The labels of all nodes of tree 1.
        :return: The sorted list of all non-terminal nodes that are in both
        derivation trees.
        """

        # Find all intersecting elements of both sets l0 and l1.
        shared_nodes = l0.intersection(l1)

        # Find only the non-terminals present in the intersecting set of
        # labels.
        shared_nodes = [i for i in shared_nodes if i in params[
            'BNF_GRAMMAR'].non_terminals]

        return sorted(shared_nodes)

    if random() > params['CROSSOVER_PROBABILITY']:
        # Crossover is not to be performed, return entire individuals.
        ind0 = p_1
        ind1 = p_0

    else:
        # Crossover is to be performed.

        if p_0.invalid:
            # The individual is invalid.
            tail_0 = []

        else:
            # Save tail of each genome.
            tail_0 = p_0.genome[p_0.used_codons:]

        if p_1.invalid:
            # The individual is invalid.
            tail_1 = []

        else:
            # Save tail of each genome.
            tail_1 = p_1.genome[p_1.used_codons:]

        # Get the set of labels of non terminals for each tree.
        labels1 = p_0.tree.get_node_labels(set())
        labels2 = p_1.tree.get_node_labels(set())

        # Find overlapping non-terminals across both trees.
        shared_nodes = intersect(labels1, labels2)

        if len(shared_nodes) != 0:
            # There are overlapping NTs, cross over parts of trees.
            ret_tree0, ret_tree1 = do_crossover(p_0.tree, p_1.tree,
                                                shared_nodes)

        else:
            # There are no overlapping NTs, cross over entire trees.
            ret_tree0, ret_tree1 = p_1.tree, p_0.tree

        # Initialise new individuals using the new trees.
        ind0 = individual.Individual(None, ret_tree0)
        ind1 = individual.Individual(None, ret_tree1)

        # Preserve tails.
        ind0.genome = ind0.genome + tail_0
        ind1.genome = ind1.genome + tail_1

    return [ind0, ind1]


def get_max_genome_index(ind_0, ind_1):
    """
    Given two individuals, return the maximum index on each genome across
    which operations are to be performed. This can be either the used
    portion of the genome or the entire length of the genome.
    
    :param ind_0: Individual 0.
    :param ind_1: Individual 1.
    :return: The maximum index on each genome across which operations are to be
             performed.
    """

    if params['WITHIN_USED']:
        # Get used codons range.

        if ind_0.invalid:
            # ind_0 is invalid. Default to entire genome.
            max_p_0 = len(ind_0.genome)

        else:
            max_p_0 = ind_0.used_codons

        if ind_1.invalid:
            # ind_1 is invalid. Default to entire genome.
            max_p_1 = len(ind_1.genome)

        else:
            max_p_1 = ind_1.used_codons

    else:
        # Get length of entire genome.
        max_p_0, max_p_1 = len(ind_0.genome), len(ind_1.genome)

    return max_p_0, max_p_1


def LTGE_crossover(p_0, p_1):
    """Crossover in the LTGE representation."""

    # crossover and repair.
    # the LTGE crossover produces one child, and is symmetric (ie
    # xover(p0, p1) is not different from xover(p1, p0)), but since it's
    # stochastic we can just run it twice to get two individuals
    # expected to be different.
    g_0, ph_0 = latent_tree_repair(
        latent_tree_crossover(p_0.genome, p_1.genome),
        params['BNF_GRAMMAR'], params['MAX_TREE_DEPTH'])
    g_1, ph_1 = latent_tree_repair(
        latent_tree_crossover(p_0.genome, p_1.genome),
        params['BNF_GRAMMAR'], params['MAX_TREE_DEPTH'])

    # wrap up in Individuals and fix up various Individual attributes
    ind_0 = individual.Individual(g_0, None, False)
    ind_1 = individual.Individual(g_1, None, False)

    ind_0.phenotype = ph_0
    ind_1.phenotype = ph_1

    # number of nodes is the number of decisions in the genome
    ind_0.nodes = ind_0.used_codons = len(g_0)
    ind_1.nodes = ind_1.used_codons = len(g_1)

    # each key is the length of a path from root
    ind_0.depth = max(len(k) for k in g_0)
    ind_1.depth = max(len(k) for k in g_1)

    # in LTGE there are no invalid individuals
    ind_0.invalid = False
    ind_1.invalid = False

    return [ind_0, ind_1]


# Set attributes for all operators to define linear or subtree representations.
variable_onepoint.representation = "linear"
fixed_onepoint.representation = "linear"
variable_twopoint.representation = "linear"
fixed_twopoint.representation = "linear"
subtree.representation = "subtree"
LTGE_crossover.representation = "latent tree"
