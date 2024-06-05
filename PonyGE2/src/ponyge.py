#! /usr/bin/env python

# PonyGE2
# Copyright (c) 2017 Michael Fenton, James McDermott,
#                    David Fagan, Stefan Forstenlechner,
#                    and Erik Hemberg
# Hereby licensed under the GNU GPL v3.
""" Python GE implementation """

from utilities.algorithm.general import check_python_version

check_python_version()

from stats.stats import get_stats
from algorithm.parameters import params, set_params
import sys
import time


def mane():
    """ Run program """
    set_params(sys.argv[1:])  # exclude the ponyge.py arg itself

    # Run evolution
    start_time = time.time()
    individuals = params['SEARCH_LOOP']()
    end_time = time.time()
    execution_time_in_minutes = (end_time - start_time) * (1 / 60)

    # Print final review
    get_stats(individuals, end=True, execution_time_in_minutes=execution_time_in_minutes)


if __name__ == "__main__":
    mane()
