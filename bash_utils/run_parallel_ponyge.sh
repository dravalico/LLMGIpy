#!/bin/bash

> bash_utils/timings_ponyge.txt

timestamp_ponyge=$(date +"%Y-%m-%dT%T")

export timestamp_ponyge

> PonyGE2/results/completed_${timestamp_ponyge}.txt

echo "PARAMS TIME_IN_SEC" >> bash_utils/timings_ponyge.txt

parallel --jobs ${2} --colsep ',' --ungroup ./bash_utils/run_single_ponyge.sh {1} :::: ${1}
