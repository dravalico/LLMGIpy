#!/bin/bash

cd /mnt/data/gpinna/damiano_pony/LLMGIpy/PonyGE2/src

python_script="ponyge.py"
arg1="--parameters improvements/G4/GPT4_problem6.txt"
output_file1="/mnt/data/gpinna/damiano_pony/LLMGIpy/times_G4_problem6.txt"
iterations=10

for ((i=1; i<=$iterations; i++)); do
    if [ $i -le 10 ]; then
        { time python "$python_script" $arg1; } 2>&1 | grep "real" >> "$output_file1"
    #else
        #{ time python "$python_script" $arg2; } 2>&1 | grep "real" >> "$output_file2"
    fi
done
