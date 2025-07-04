import numpy as np
from llmpony.pony.algorithm.parameters import params
from llmpony.pony.representation import individual


# =========================================

def format_program(individual, header, footer):
    """formats the program by formatting the individual and adding
    a header and footer"""
    last_new_line = header.rindex('\n')
    # indent = header[last_new_line + len('\n'):len(header)]
    # individual1 = individual[3:]
    # individual1 = individual1[:-2]
    individual = individual.replace('#', '\n')
    individual = individual.replace("print", "")  # HACK
    return header + format_individual(individual) + footer

def format_individual(code, additional_indent=""):
    """format individual by adding appropriate indentation and loop break
    statements"""
    INDENTSPACE = "  "
    LOOPBREAK = "loopBreak"
    LOOPBREAKUNNUMBERED = "loopBreak%"
    LOOPBREAK_INITIALISE = "loopBreak% = 0"
    LOOPBREAK_IF = "if loopBreak% >"
    LOOPBREAK_INCREMENT = "loopBreak% += 1"
    FORCOUNTER = "forCounter"
    FORCOUNTERUNNUMBERED = "forCounter%"

    parts = code.split('\n')
    indent = 0
    string_builder = ""
    for_counter_number = 0
    first = True
    for part in parts:
        line = part.strip()
        # remove indentation if bracket is at the beginning of the line
        while line.startswith(":}"):
            indent -= 1
            line = line[2:].strip()

        # add indent
        if not first:
            string_builder += additional_indent
        else:
            first = False

        for i in range(0, indent):
            string_builder += INDENTSPACE

        # add indentation
        while line.endswith("{:"):
            indent += 1
            line = line[:len(line) - 2].strip()
        # remove indentation if bracket is at the end of the line
        while line.endswith(":}"):
            indent -= 1
            line = line[:len(line) - 2].strip()

        if LOOPBREAKUNNUMBERED in line:
            if LOOPBREAK_INITIALISE in line:
                line = ""  # remove line
            elif LOOPBREAK_IF in line:
                line = line.replace(LOOPBREAKUNNUMBERED,
                                    LOOPBREAK)
            elif LOOPBREAK_INCREMENT in line:
                line = line.replace(LOOPBREAKUNNUMBERED,
                                    LOOPBREAK)
            else:
                raise Exception("Python 'while break' is malformed.")
        elif FORCOUNTERUNNUMBERED in line:
            line = line.replace(FORCOUNTERUNNUMBERED,
                                FORCOUNTER + str(for_counter_number))
            for_counter_number += 1

        # add line to code
        string_builder += line
        string_builder += '\n'
    return string_builder

# =========================================


def check_ind(ind, check):
    """
    Check all shallow aspects of an individual to ensure everything is correct.
    
    :param ind: An individual to be checked.
    :return: False if everything is ok, True if there is an issue.
    """

    if ind.genome == []:
        # Ensure all individuals at least have a genome.
        return True

    if ind.invalid and \
            ((check == "crossover" and params['NO_CROSSOVER_INVALIDS']) or
             (check == "mutation" and params['NO_MUTATION_INVALIDS'])):
        # We have an invalid.
        return True

    elif params['MAX_TREE_DEPTH'] and ind.depth > params['MAX_TREE_DEPTH']:
        # Tree is too deep.
        return True

    elif params['MAX_TREE_NODES'] and ind.nodes > params['MAX_TREE_NODES']:
        # Tree has too many nodes.
        return True

    elif params['MAX_GENOME_LENGTH'] and len(ind.genome) > \
            params['MAX_GENOME_LENGTH']:
        # Genome is too long.
        return True


def check_genome_mapping(ind):
    """
    Re-maps individual to ensure genome is correct, i.e. that it maps to the
    correct phenotype and individual.
    
    :param ind: An instance of the representation.individual.Individual class.
    :return: Nothing.
    """

    # Re-map individual using fast genome mapper to check everything is ok
    new_ind = individual.Individual(ind.genome, None)

    # Get attributes of both individuals.
    attributes_0 = vars(ind)
    attributes_1 = vars(new_ind)

    if params['GENOME_OPERATIONS']:
        # If this parameter is set then the new individual will have no tree.
        attributes_0['tree'] = None

    else:
        if attributes_0['tree'] != attributes_1['tree']:
            s = "utilities.representation.check_methods.check_ind.\n" \
                "Error: Individual trees do not match."
            raise Exception(s)

    # Check that all attributes match across both individuals.
    for a_0 in sorted(attributes_0.keys()):
        for a_1 in sorted(attributes_1.keys()):
            if a_0 == a_1 and attributes_0[a_0] != attributes_1[a_1] and not \
                    (type(attributes_0[a_0]) is float and
                     type(attributes_1[a_1]) is float and
                     np.isnan(attributes_0[a_0]) and
                     np.isnan(attributes_1[a_1])):
                s = "utilities.representation.check_methods." \
                    "check_genome_mapping\n" \
                    "Error: Individual attributes do not match genome-" \
                    "encoded attributes.\n" \
                    "       Original attribute:\n" \
                    "           %s :\t %s\n" \
                    "       Encoded attribute:\n" \
                    "           %s :\t %s" % \
                    (a_0, attributes_0[a_0], a_1, attributes_1[a_1])
                raise Exception(s)


def check_ind_from_parser(ind, target):
    """
    Checks the mapping of an individual generated by the GE parser against
    the specified target string to ensure the GE individual is correct.

    :param ind: An instance of the representation.individual.Individual class.
    :param target: A target string against which to match the phenotype of
    the individual.
    :return: Nothing.
    """

    # Re-map individual using genome mapper to check everything is ok.
    new_ind = individual.Individual(ind.genome, None)

    # Check phenotypes are the same.
    if new_ind.phenotype != ind.phenotype:
        s = "utilities.representation.check_methods.check_ind_from_parser\n" \
            "Error: Solution phenotype doesn't match genome mapping.\n" \
            "       Solution phenotype:  \t %s\n" \
            "       Solution from genome:\t %s\n" \
            "       Derived genome:      \t %s" % \
            (ind.phenotype, new_ind.phenotype, ind.genome)
        raise Exception(s)

    # Check the phenotype matches the target string.
    elif ind.phenotype != target:
        s = "utilities.representation.check_methods.check_ind_from_parser\n" \
            "Error: Solution phenotype doesn't match target.\n" \
            "       Target:   \t %s\n" \
            "       Solution: \t %s" % (target, ind.phenotype)
        raise Exception(s)

    else:
        # Check the tree matches the phenotype.
        check_genome_mapping(ind)


def check_genome_from_tree(ind_tree):
    """
    Goes through a tree and checks each codon to ensure production choice is
    correct.
    
    :param ind_tree: The representation.tree.Tree class derivation tree of
    an individual.
    :return: Nothing.
    """

    if ind_tree.children:
        # This node has children and thus must have an associated codon.

        if not ind_tree.codon:
            s = "utilities.representation.check_methods." \
                "check_genome_from_tree\n" \
                "Error: Node with children has no codon.\n" \
                "       %s" % (str(ind_tree.children))
            raise Exception(s)

        # Check production choices for node root.
        productions = params['BNF_GRAMMAR'].rules[ind_tree.root]['choices']

        # Select choice based on node codon.
        selection = ind_tree.codon % len(productions)
        chosen_prod = productions[selection]

        # Build list of roots of the chosen production.
        prods = [prod['symbol'] for prod in chosen_prod['choice']]
        roots = []

        # Build list of the roots of all node children.
        for kid in ind_tree.children:
            roots.append(kid.root)

        # Match production roots with children roots.
        if roots != prods:
            s = "utilities.representation.check_methods." \
                "check_genome_from_tree\n" \
                "Error: Codons are incorrect for given tree.\n" \
                "       Codon productions:\t%s\n       " \
                "       Actual children:\t%s" % (str(prods), str(roots))
            raise Exception(s)

    for kid in ind_tree.children:
        # Recurse over all children.
        check_genome_from_tree(kid)


def check_expansion(tree, nt_keys):
    """
    Check if a given tree is completely expanded or not. Return boolean
    True if the tree IS NOT completely expanded, i.e. if tree is invalid.
    
    :param tree: An individual's derivation tree.
    :param nt_keys: The list of all non-terminals.
    :return: True if tree is not fully expanded, else False.
    """

    check = False
    if tree.root in nt_keys:
        # Current node is a NT and should have children
        if tree.children:
            # Everything is as expected
            for child in tree.children:
                # Recurse over all children.
                check = child.check_expansion(nt_keys)

                if check:
                    # End recursion.
                    break

        else:
            # Current node is not completely expanded.
            check = True

    return check


def build_genome(tree, genome):
    """
    Goes through a tree and builds a genome from all codons in the subtree.

    :param tree: An individual's derivation tree.
    :param genome: The list of all codons in a subtree.
    :return: The fully built genome of a subtree.
    """

    if tree.codon:
        # If the current node has a codon, append it to the genome.
        genome.append(tree.codon)

    for child in tree.children:
        # Recurse on all children.
        genome = child.build_genome(genome)

    return genome


def get_nodes_and_depth(tree, nodes=0, max_depth=0):
    """
    Get the number of nodes and the max depth of the tree.
    
    :param tree: An individual's derivation tree.
    :param nodes: The number of nodes in a tree.
    :param max_depth: The maximum depth of any node in the tree.
    :return: number, max_depth.
    """

    # Increment number of nodes in the tree.
    nodes += 1

    # Set the depth of the current node.
    if tree.parent:
        tree.depth = tree.parent.depth + 1
    else:
        tree.depth = 1

    # Check the recorded max_depth.
    if tree.depth > max_depth:
        max_depth = tree.depth

    # Create list of all non-terminal children of current node.
    NT_kids = [kid for kid in tree.children if kid.root in
               params['BNF_GRAMMAR'].non_terminals]

    if not NT_kids and get_output(tree):
        # Current node has only terminal children.
        nodes += 1

        # Terminal children increase the current node depth by one.
        # Check the recorded max_depth.
        if tree.depth + 1 > max_depth:
            max_depth = tree.depth + 1

    else:
        for child in NT_kids:
            # Recurse over all children.
            nodes, max_depth = get_nodes_and_depth(child, nodes, max_depth)

    return nodes, max_depth


def get_max_tree_depth(tree, max_depth=1):
    """
    Returns the maximum depth of the tree from the current node.

    :param tree: The tree we wish to find the maximum depth of.
    :param max_depth: The maximum depth of the tree.
    :return: The maximum depth of the tree.
    """

    curr_depth = get_current_depth(tree)
    if curr_depth > max_depth:
        max_depth = curr_depth
    for child in tree.children:
        max_depth = get_max_tree_depth(child, max_depth)
    return max_depth


def get_current_depth(tree):
    """
    Get the depth of the current node by climbing back up the tree until no
    parents remain (i.e. the root node has been reached).

    :param tree: An individual's derivation tree.
    :return: The depth of the current node.
    """

    # Set the initial depth at 1.
    depth = 1

    # Set the current parent.
    current_parent = tree.parent

    while current_parent is not None:
        # Recurse until the root node of the tree has been reached.

        # Increment depth.
        depth += 1

        # Set new parent.
        current_parent = current_parent.parent

    return depth


def get_output(ind_tree):
    """
    Calls the recursive build_output(self) which returns a list of all
    node roots. Joins this list to create the full phenotype of an
    individual. This two-step process speeds things up as it only joins
    the phenotype together once rather than at every node.

    :param ind_tree: a full tree for which the phenotype string is to be built.
    :return: The complete built phenotype string of an individual.
    """

    def build_output(tree):
        """
        Recursively adds all node roots to a list which can be joined to
        create the phenotype.

        :return: The list of all node roots.
        """

        output = []
        for child in tree.children:
            if not child.children:
                # If the current child has no children it is a terminal.
                # Append it to the output.
                output.append(child.root)

            else:
                # Otherwise it is a non-terminal. Recurse on all
                # non-terminals.
                output += build_output(child)

        return output

    return "".join(build_output(ind_tree))


def ret_true(obj):
    """
    Returns "True" if an object is there. E.g. if given a list, will return
    True if the list contains some data, but False if the list is empty.
    
    :param obj: Some object (e.g. list)
    :return: True if something is there, else False.
    """

    if obj:
        return True
    else:
        return False


def generate_codon(NT, choice):
    """
    Given a list of choices and a choice from that list, generate and return a
    codon which will result in that production choice being made.

    :param NT: A root non-terminal node from which production choices are made.
    :param choice: A production choice from the available choices of the
    given NT.
    :return: A codon that will give that production choice.
    """

    productions = params['BNF_GRAMMAR'].rules[NT]

    # Find the production choices from the given NT.
    choices = [choice['choice'] for choice in productions['choices']]

    # Find the index of the chosen production and set a matching codon based
    # on that index.
    prod_index = choices.index(choice)

    codon = productions['no_choices'] + prod_index

    # Generate a valid codon.
    return codon


def check_tree(tree):
    """
    Recursively traverse a tree and ensure that all parents and children are
    correct.
    
    :param tree: A tree.
    :return: Nothing.
    """

    if tree.children:

        if not tree.codon:
            s = "utilities.representation.check_methods.check_tree\n" \
                "Error: Node with children has no associated codon."
            raise Exception(s)

        for child in tree.children:

            if child.parent != tree:
                s = "utilities.representation.check_methods.check_tree\n" \
                    "Error: Child doesn't belong to parent.\n" \
                    "       Child parent:  %s\n" \
                    "       Actual parent: %s\n" \
                    "       Child P depth: %s\n" \
                    "       Parent depth:  %s" % \
                    (child.parent.root, tree.root,
                     child.parent.depth, tree.depth)
                raise Exception(s)

            else:
                check_tree(child)
