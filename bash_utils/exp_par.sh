#!/bin/bash

cd LLMGIpy/PonyGE2/src/

python_script="ponyge.py"
arg="--parameters improvements/"
output_file=""
iterations=5

run_python_script() {
    iteration="$1"
    { time python "$python_script" $arg; } 2>&1 | grep "real"
}

exec 9>>"$output_file"
flock -n 9 || exit 1

for ((i=1; i<=$iterations; i++)); do
    run_python_script "$i" >> "$output_file" &
done

wait

exec 9>&-
