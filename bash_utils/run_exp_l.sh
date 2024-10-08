#!/bin/bash

cd src
problem_benchmarks=("psb2" "humaneval")
models=("Gemma2B" "CodeGemma7B" "LLaMA38B" "CodeLLaMA7B" "Mistral7B")
train_sizes=(20 40 60)

for problem_benchmark in ${problem_benchmarks[@]}
do
	for train_size in ${train_sizes[@]}
	do
		for model in ${models[@]}
		do
			start=$(date +%s)
			python3 main.py --model ${model} --dataset ${problem_benchmark} --prompt_type "text" --train_size ${train_size}  --iterations 10
			end=$(date +%s)
			echo "${problem_benchmark} ${train_size} ${model} 0 $(( end - start ))" >> ../bash_utils/timings.txt
		done
	done
done
