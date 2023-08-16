from random import choice, randint, randrange

from algorithm.parameters import params
from representation.tree import Tree
from utilities.representation.check_methods import get_nodes_and_depth, \
    ret_true


def generate_tree(tree, genome, output, method, nodes, depth, max_depth,
                  depth_limit):
    """
    Recursive function to derive a tree using a given method.
    
    :param tree: An instance of the Tree class.
    :param genome: The list of all codons in a tree.
    :param output: The list of all terminal nodes in a subtree. This is
    joined to become the phenotype.
    :param method: A string of the desired tree derivation method,
    e.g. "full" or "random".
    :param nodes: The total number of nodes in the tree.
    :param depth: The depth of the current node.
    :param max_depth: The maximum depth of any node in the tree.
    :param depth_limit: The maximum depth the tree can expand to.
    :return: genome, output, nodes, depth, max_depth.
    """

    # Increment nodes and depth, set depth of current node.
    nodes += 1
    depth += 1
    tree.depth = depth

    # Find the productions possible from the current root.
    productions = params['BNF_GRAMMAR'].rules[tree.root]

    if depth_limit:
        # Set remaining depth.
        remaining_depth = depth_limit - depth

    else:
        remaining_depth = depth_limit

    # Find which productions can be used based on the derivation method.
    available = legal_productions(method, remaining_depth, tree.root,
                                  productions['choices'])

    # Randomly pick a production choice and make a codon with it.
    chosen_prod = choice(available)
    codon = generate_codon(chosen_prod, productions)
    
    # Set the codon for the current node and append codon to the genome.
    tree.codon = codon
    genome.append(codon)

    # Initialise empty list of children for current node.
    tree.children = []

    for symbol in chosen_prod['choice']:
        # Iterate over all symbols in the chosen production.
        if symbol["type"] == "T":
            # The symbol is a terminal. Append new node to children.
            tree.children.append(Tree(symbol["symbol"], tree))

            # Append the terminal to the output list.
            output.append(symbol["symbol"])

        elif symbol["type"] == "NT":
            # The symbol is a non-terminal. Append new node to children.
            tree.children.append(Tree(symbol["symbol"], tree))

            # recurse on the new node.
            genome, output, nodes, d, max_depth = \
                generate_tree(tree.children[-1], genome, output, method,
                              nodes, depth, max_depth, depth_limit)

    NT_kids = [kid for kid in tree.children if kid.root in
               params['BNF_GRAMMAR'].non_terminals]

    if not NT_kids:
        # Then the branch terminates here
        depth += 1
        nodes += 1

    if depth > max_depth:
        # Set new maximum depth
        max_depth = depth

    return genome, output, nodes, depth, max_depth


def generate_codon(chosen_prod, productions):
    """
    Generate a single codon
    
    :param chosen_prod: the specific production to build a codon for
    :param productions: productions possible from the current root
    :return: a codon integer
    
    """

    # Find the index of the chosen production
    production_index = productions['choices'].index(chosen_prod)

    # Choose a random offset with guarantee that (offset + production_index) < codon_size
    offset = randrange(
        start=0,
        stop=params['BNF_GRAMMAR'].codon_size - productions['no_choices'] + 1,
        step=productions['no_choices']
    )

    codon = offset + production_index
    return codon


def legal_productions(method, depth_limit, root, productions):
    """
    Returns the available production choices for a node given a specific
    depth limit.
    
    :param method: A string specifying the desired tree derivation method.
    Current methods are "random" or "full".
    :param depth_limit: The overall depth limit of the desired tree from the
    current node.
    :param root: The root of the current node.
    :param productions: The full list of production choices from the current
    root node.
    :return: The list of available production choices based on the specified
    derivation method.
    """

    # Get all information about root node
    root_info = params['BNF_GRAMMAR'].non_terminals[root]

    if method == "random":
        # Randomly build a tree.
        
        if depth_limit is None:
            # There is no depth limit, any production choice can be used.
            available = productions

        elif depth_limit > params['BNF_GRAMMAR'].max_arity + 1:
            # If the depth limit is greater than the maximum arity of the
            # grammar, then any production choice can be used.
            available = productions

        elif depth_limit < 0:
            # If we have already surpassed the depth limit, then list the
            # choices with the shortest terminating path.
            available = root_info['min_path']

        else:
            # The depth limit is less than or equal to the maximum arity of
            # the grammar + 1. We have to be careful in selecting available
            # production choices lest we generate a tree which violates the
            # depth limit.
            available = [prod for prod in productions if prod['max_path'] <=
                         depth_limit - 1]

            if not available:
                # There are no available choices which do not violate the depth
                # limit. List the choices with the shortest terminating path.
                available = root_info['min_path']

    elif method == "full":
        # Build a "full" tree where every branch extends to the depth limit.

        if not depth_limit:
            # There is no depth limit specified for building a Full tree.
            # Raise an error as a depth limit HAS to be specified here.
            s = "representation.derivation.legal_productions\n" \
                "Error: Depth limit not specified for `Full` tree derivation."
            raise Exception(s)

        elif depth_limit > params['BNF_GRAMMAR'].max_arity + 1:
            # If the depth limit is greater than the maximum arity of the
            # grammar, then only recursive production choices can be used.
            available = root_info['recursive']

            if not available:
                # There are no recursive production choices for the current
                # rule. Pick any production choices.
                available = productions

        else:
            # The depth limit is less than or equal to the maximum arity of
            # the grammar + 1. We have to be careful in selecting available
            # production choices lest we generate a tree which violates the
            # depth limit.
            available = [prod for prod in productions if prod['max_path'] ==
                         depth_limit - 1]

            if not available:
                # There are no available choices which extend exactly to the
                # depth limit. List the NT choices with the longest terminating
                # paths that don't violate the limit.
                available = [prod for prod in productions if prod['max_path']
                             < depth_limit - 1]

    return available


def pi_random_derivation(tree, max_depth):
    """
    Randomly builds a tree from a given root node up to a maximum given
    depth. Uses position independent methods to derive non-terminal nodes.
    Final tree is not guaranteed to reach the specified max_depth limit.
    
    :param tree: An instance of the representation.tree.Tree class.
    :param max_depth: The maximum depth to which to derive a tree.
    :return: The fully derived tree.
    """

    # Initialise derivation queue.
    queue = [[tree, ret_true(params['BNF_GRAMMAR'].non_terminals[
                                 tree.root]['recursive'])]]

    # Initialise empty genome. With PI operators we can't use a depth-first
    # traversal of the tree to build the genome, we need to build it as we
    # encounter each node.
    genome = []

    while queue:
        # Loop until no items remain in the queue.

        # Pick a random item from the queue.
        chosen = randint(0, len(queue) - 1)

        # Pop the next item from the queue.
        all_node = queue.pop(chosen)
        node = all_node[0]

        # Get depth current node.
        if node.parent is not None:
            node.depth = node.parent.depth + 1

        # Find the productions possible from the current root.
        productions = params['BNF_GRAMMAR'].rules[node.root]

        # Set remaining depth.
        remaining_depth = max_depth - node.depth

        # Find which productions can be used based on the derivation method.
        available = legal_productions("random", remaining_depth, node.root,
                                      productions['choices'])

        # Randomly pick a production choice and make a codon with it.
        chosen_prod = choice(available)
        codon = generate_codon(chosen_prod, productions)

        # Set the codon for the current node and append codon to the genome.
        node.codon = codon

        # Insert codon into the genome.
        genome.append(codon)

        # Initialise empty list of children for current node.
        node.children = []

        for i, symbol in enumerate(chosen_prod['choice']):
            # Iterate over all symbols in the chosen production.

            # Create new child.
            child = Tree(symbol["symbol"], node)

            # Append new node to children.
            node.children.append(child)

            if symbol["type"] == "NT":
                # The symbol is a non-terminal.

                # Check whether child is recursive
                recur_child = ret_true(params['BNF_GRAMMAR'].non_terminals
                                       [child.root]['recursive'])

                # Insert new child into the correct position in the queue.
                queue.insert(chosen + i, [child, recur_child])

    # genome, output, invalid, depth, and nodes can all be generated by
    # recursing through the tree once.
    _, output, invalid, depth, \
    nodes = tree.get_tree_info(params['BNF_GRAMMAR'].non_terminals.keys(),
                               [], [])

    return genome, output, nodes, depth


def pi_grow(tree, max_depth):
    """
    Grows a tree until a single branch reaches a specified depth. Does this
    by only using recursive production choices until a single branch of the
    tree has reached the specified maximum depth. After that any choices are
    allowed.
    
    :param tree: An instance of the representation.tree.Tree class.
    :param max_depth: The maximum depth to which to derive a tree.
    :return: The fully derived tree.
    """

    # Initialise derivation queue.
    queue = [[tree, ret_true(params['BNF_GRAMMAR'].non_terminals[
                                 tree.root]['recursive'])]]

    # Initialise empty genome. With PI operators we can't use a depth-first
    # traversal of the tree to build the genome, we need to build it as we
    # encounter each node.
    genome = []

    while queue:
        # Loop until no items remain in the queue.

        # Pick a random item from the queue.
        chosen = randint(0, len(queue) - 1)

        # Pop the next item from the queue.
        all_node = queue.pop(chosen)
        node, recursive = all_node[0], all_node[0]

        # Get depth of current node.
        if node.parent is not None:
            node.depth = node.parent.depth + 1

        # Get maximum depth of overall tree.
        _, overall_depth = get_nodes_and_depth(tree)

        # Find the productions possible from the current root.
        productions = params['BNF_GRAMMAR'].rules[node.root]

        # Set remaining depth.
        remaining_depth = max_depth - node.depth

        if (overall_depth < max_depth) or \
                (recursive and (not any([item[1] for item in queue]))):
            # We want to prevent the tree from creating terminals until a
            # single branch has reached the full depth. Only select recursive
            # choices.

            # Find which productions can be used based on the derivation
            # method.
            available = legal_productions("full", remaining_depth, node.root,
                                          productions['choices'])
        else:
            # Any production choices can be made.

            # Find which productions can be used based on the derivation
            # method.
            available = legal_productions("random", remaining_depth, node.root,
                                          productions['choices'])

        # Randomly pick a production choice and make a codon with it.
        chosen_prod = choice(available)
        codon = generate_codon(chosen_prod, productions)

        # Set the codon for the current node and append codon to the genome.
        node.codon = codon

        # Insert codon into the genome.
        genome.append(codon)

        # Initialise empty list of children for current node.
        node.children = []

        for i, symbol in enumerate(chosen_prod['choice']):
            # Iterate over all symbols in the chosen production.

            # Create new child.
            child = Tree(symbol["symbol"], node)

            # Append new node to children.
            node.children.append(child)

            if symbol["type"] == "NT":
                # The symbol is a non-terminal.

                # Check whether child is recursive
                recur_child = ret_true(params['BNF_GRAMMAR'].non_terminals
                                       [child.root]['recursive'])

                # Insert new child into the correct position in the queue.
                queue.insert(chosen + i, [child, recur_child])

    # genome, output, invalid, depth, and nodes can all be generated by
    # recursing through the tree once.
    _, output, invalid, depth, \
    nodes = tree.get_tree_info(params['BNF_GRAMMAR'].non_terminals.keys(),
                               [], [])

    return genome, output, nodes, depth
