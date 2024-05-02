#!/bin/bash

cd PonyGE2/src

python_script="ponyge.py"
files=("improvements/ChG/ChatGPT_problem1.txt" "improvements/ChG/ChatGPT_problem3.txt" "improvements/ChG/ChatGPT_problem5.txt" "improvements/ChG/ChatGPT_problem6.txt" "improvements/ChG/ChatGPT_problem7.txt" "improvements/ChG/ChatGPT_problem13.txt" "improvements/ChG/ChatGPT_problem14.txt" "improvements/ChG/ChatGPT_problem17.txt" "improvements/ChG/ChatGPT_problem18.txt" "improvements/ChG/ChatGPT_problem19.txt" "improvements/ChG/ChatGPT_problem24.txt")
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
