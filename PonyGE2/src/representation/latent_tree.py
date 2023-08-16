"""Latent-Tree GE (LTGE)

Alberto Moraglio and James McDermott 2018.

This is still GE, with integer genomes, but integers arranged in a
dictionary. In the dictionary of key-value pairs, each key is a list
of tuples representing a path from the root to the node, and the
corresponding value is an integer which (still) represents the choice
of production made at the node. We call it latent tree GE because the
representation itself is "flat" (a dictionary) but the derivation tree
is implicit or latent.

Example genome with interpretation:

{
(): 8, # at the root, choice 8 was made
((8, 1),): 5, # for the first symbol in choice 8, choice 5 was made
((8, 1), (5, 1)): 4,
((8, 1), (5, 1), (4, 1)): 9
}


The initialisation operator in LTGE is equivalent to that in GE.
The mutation operator is equivalent to the CFG-GP mutation.  The
crossover operator is equivalent to a homologous crossover on
derivation trees.

"""

import random

from algorithm.parameters import params
from representation.derivation import legal_productions


def latent_tree_random_ind(grammar, maxdepth, old_genome=None):
    """Generate a random individual (genome and string), OR repair a
    genome and generate its string. These two things are conceptually
    distinct, but they share almost all code. The idea is that
    repairing a genome consists of traversing it and using its choices
    where they are appropriate, and otherwise generating new choices
    (and any old, unused choices will be discarded). Generating a new
    individual just means that there are no appropriate choices, so
    always generating new choices. So, we implement both in the same
    function."""

    # we use this inner helper function to do the work.
    # it "accumulates" the genome as it runs.
    def _random_ind(gram, genome, depth, s=None, name=None):
        """Recursively create a genome. gram is a grammar, genome a dict
        (initially empty), depth an integer giving maximum depth. s is
        the current symbol (None tells us to use the start symbol.) name
        is the name-in-progress."""
        if s is None:
            s = gram.start_rule["symbol"]
            name = tuple()
        elif s in gram.terminals:
            return s

        rule = gram.rules[s]

        if old_genome and name in old_genome:

            # A valid entry was found in old_genome. Apply mod rule as
            # part of repair: it will have no effect if the value is
            # already in the right range.
            gi = old_genome[name] % len(rule['choices'])
            prod = rule['choices'][gi]

        else:

            # No valid entry was found, so choose a production from
            # among those which are legal (because their min depth to
            # finish recursion is less than or equal to max depth
            # minus our current depth).
            productions = params['BNF_GRAMMAR'].rules[s]
            available = legal_productions("random", depth, s,
                                          productions['choices'])
            prod = random.choice(available)  # choose production
            gi = productions['choices'].index(prod)  # find its index

        genome[name] = gi

        # Join together all the strings for this production. For
        # terminals just use the string itself. For non-terminals,
        # recurse: decrease depth, pass in the symbol, and append to
        # the naming scheme according to the choice we made in the
        # current call. Recall that each symbol s is a dict:
        # s["symbol"] is the symbol itself, s["type"] is 'T' or 'NT'.
        return "".join((s["symbol"] if s["type"] == "T"
                        else
                        _random_ind(gram,
                                    genome,
                                    depth - 1,
                                    s["symbol"],
                                    name + ((gi, i),)))
                       for i, s in enumerate(prod['choice']))

    genome = {}
    s = _random_ind(grammar, genome, maxdepth, None, None)
    return genome, s


def latent_tree_repair(genome, gram, maxdepth):
    """Given a genome, make any necessary repairs. This could include
    discarding unused genetic material, generating new material, and
    taking the 'mod' of existing values. It is just a wrapper on
    random_ind which does all the work. It re-orders the arguments
    since the object of the verb repair is the thing to be repaired
    (the genome) whereas in random_ind the genome is an optional final
    argument."""
    return latent_tree_random_ind(gram, maxdepth, genome)


def latent_tree_crossover(g1, g2):
    """Produce a single child genome by crossover through dict
    manipulation. For each key: if present in both parents, then
    choose value randomly; if present in only one parent, then use
    that. Later, repair must make sure the offspring is valid."""

    # Put all of g1 in, to start with. FIXME The deep_copy() in
    # crossover_inds() ought to guarantee us that g1 and g2 are
    # copies, not original members of the population so we can edit
    # them in-place. However, I'm finding that c = g1 is giving
    # different results from c = g1.copy(). I've checked that
    # deep_copy() is actually running, so I don't understand this
    # problem. To be on the safe side, we'll keep the copy() here.
    # See https://github.com/PonyGE/PonyGE2/issues/89.
    c = g1.copy()
    for k in g2.keys():
        if k in g1:
            # k is in both parents so choose randomly.
            c[k] = random.choice((g1[k], g2[k]))
        else:
            # for items in g2 only, copy them in
            c[k] = g2[k]
    return c


def latent_tree_mutate(g):
    """Produce an offspring genome by mutation through dict
    manipulation. Choose a random key in the dict, and overwrite its
    value with a random int. Later, repair must make sure the
    offspring is valid, including using the mod rule to map from a
    (possibly) large int to the corresponding small one (ie the one
    giving the same production choice) in the range of possible
    choices."""

    # FIXME We don't rely on g being a copy, in case the search
    # algorithm sometimes mutates individuals which are original
    # members of the population.
    # See https://github.com/PonyGE/PonyGE2/issues/89.
    g = g.copy()
    k = random.choice(list(g.keys()))
    g[k] = random.randrange(1000000)  # there is no true maxint on py 3
    return g
