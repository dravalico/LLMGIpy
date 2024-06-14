#!/bin/bash

> bash_utils/timings_ponyge.txt

echo "PARAMS TIME_IN_SEC" >> bash_utils/timings_ponyge.txt

parallel --colsep ',' --ungroup ./bash_utils/run_single_ponyge.sh {1} :::: ${1}
