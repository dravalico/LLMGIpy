from sys import path

path.append("../src")

from utilities.algorithm.general import check_python_version

check_python_version()

from algorithm.parameters import params
import utilities.algorithm.command_line_parser as parser
from representation.grammar import Grammar
from utilities.fitness.math_functions import sci_notation

import sys
import os


def main(command_line_args):
    """
    Given a specified grammar file, parse the grammar using the Grammar class
    and print out the number of unique permutations and combinations of
    distinct phenotypes that this grammar is capable of generating at a
    number of given depths.

    :return: Nothing.
    """

    # Parse command line args (we only want the grammar file)
    cmd_args, unknown = parser.parse_cmd_args(command_line_args)

    # Join original params dictionary with command line specified arguments.
    # NOTE that command line arguments overwrite all previously set parameters.
    params.update(cmd_args)

    # Parse grammar file and set grammar class.
    grammar = Grammar(os.path.join("..", "grammars", params['GRAMMAR_FILE']))

    print("\nSpecified grammar:", params['GRAMMAR_FILE'])

    # Initialise zero maximum branching factor for grammar
    max_b_factor = 0

    print("\nBranching factor for each non-terminal:")

    for NT in sorted(grammar.non_terminals.keys()):

        # Get branching factor for current NT.
        b_factor = grammar.non_terminals[NT]['b_factor']

        # Print info.
        print("", NT, "   \t:", b_factor)

        # Set maximum branching factor.
        if b_factor > max_b_factor:
            max_b_factor = b_factor

    print("\nMaximum branching factor of the grammar:", max_b_factor)

    # Initialise counter for the total number of solutions.
    total_solutions = 0

    print("\nNumber of unique possible solutions for a range of depths:\n")

    for depth in grammar.permutations:
        # Get number of solutions possible at current depth
        solutions = grammar.permutations[depth]

        print(" Depth: %d \t Number of unique solutions: %s" %
              (depth, sci_notation(solutions)))

        # Increment total number of solutions.
        total_solutions += solutions

    print("\nTotal number of unique possible solutions that can be generated"
          "up to and including a depth of %d: %s" %
          (depth, sci_notation(total_solutions)))


if __name__ == "__main__":
    # Do not write or save any files.
    params['DEBUG'] = True

    # Run main program.
    main(sys.argv[1:])  # exclude the ponyge.py arg itself
