#!/bin/bash

> bash_utils/timings_ponyge.txt
> PonyGE2/results/terminal_std_out.txt

echo "PARAMS TIME_IN_SEC" >> bash_utils/timings_ponyge.txt

parallel --jobs ${2} --colsep ',' --ungroup ./bash_utils/run_single_ponyge.sh {1} :::: ${1}
