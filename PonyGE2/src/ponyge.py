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
import os
import datetime
import traceback
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def mane():
    try:
        if not os.path.isdir("../results/"):
            os.makedirs("../results/", exist_ok=True)

        if not os.path.isdir("../run_with_exceptions/"):
            os.makedirs("../run_with_exceptions/", exist_ok=True)

        """ Run program """
        set_params(sys.argv[1:])  # exclude the ponyge.py arg itself

        if 'TIMESTAMP_PONYGE' not in params:
            params['TIMESTAMP_PONYGE'] = str(datetime.datetime.now())

        # Run evolution
        start_time = time.time()
        individuals = params['SEARCH_LOOP']()
        end_time = time.time()
        execution_time_in_minutes = (end_time - start_time) * (1 / 60)

        # Print final review
        get_stats(individuals, end=True, execution_time_in_minutes=execution_time_in_minutes)

        with open(os.path.join("../results/", f'completed_{params["TIMESTAMP_PONYGE"]}.txt'), 'a+') as terminal_std_out:
            terminal_std_out.write(f'{params["PARAMETERS"]}')
            terminal_std_out.write('\n')
    except Exception as e:
        error_string = str(traceback.format_exc())
        with open(f'../run_with_exceptions/{params["PARAMETERS"].replace("/", "___")}', 'w') as f:
            f.write(error_string)

if __name__ == "__main__":
    mane()
