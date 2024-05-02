#!/bin/bash

cd PonyGE2/src

python_script="ponyge.py"
files=("improvements/G4/GPT4_problem1.txt" "improvements/G4/GPT4_problem2.txt" "improvements/G4/GPT4_problem3.txt" "improvements/G4/GPT4_problem5.txt" "improvements/G4/GPT4_problem6.txt" "improvements/G4/GPT4_problem7.txt" "improvements/G4/GPT4_problem13.txt" "improvements/G4/GPT4_problem14.txt" "improvements/G4/GPT4_problem17.txt" "improvements/G4/GPT4_problem18.txt" "improvements/G4/GPT4_problem19.txt" "improvements/G4/GPT4_problem24.txt")
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
