#!/bin/bash

cd PonyGE2/src

python_script="ponyge.py"
files=("improvements/A13/Alpaca13B_problem0.txt" "improvements/A13/Alpaca13B_problem2.txt" "improvements/A13/Alpaca13B_problem3.txt" "improvements/A13/Alpaca13B_problem5.txt" "improvements/A13/Alpaca13B_problem8.txt" "improvements/A13/Alpaca13B_problem11.txt" "improvements/A13/Alpaca13B_problem12.txt" "improvements/A13/Alpaca13B_problem13.txt" "improvements/A13/Alpaca13B_problem14.txt" "improvements/A13/Alpaca13B_problem15.txt" "improvements/A13/Alpaca13B_problem16.txt" "improvements/A13/Alpaca13B_problem17.txt" "improvements/A13/Alpaca13B_problem18.txt" "improvements/A13/Alpaca13B_problem20.txt" "improvements/A13/Alpaca13B_problem21.txt" "improvements/A13/Alpaca13B_problem22.txt")
output_directory="/mnt/data/gpinna/damiano_pony/LLMGIpy/"

iterations=10
echo "ok"

for file in "${files[@]}"; do
    file_name=$(basename $file)
    output_file="$output_directory/times_$file_name.txt"
    for ((i=1; i<=$iterations; i++)); do
        { time python "$python_script" "--parameters" "$file"; } 2>&1 | grep "real" >> "$output_file"
    done
done
