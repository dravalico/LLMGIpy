#!/bin/bash

# THIS SCRIPT MUST BE PLACED WITHIN AN "L" FOLDER OF EITHER SEEDS SEEDS_METADATA OR GRAMMARS/DYNAMIC TO COPY PASTE THE SEEDS AND GRAMMARS FOR A GIVEN TRAIN SIZE AND REPLICATE THEM FOR OTHER TRAIN SIZES.
# CAREFULLY CHECK THE CONTENT OF THIS SCRIPT BEFORE COPYING AND EXECUTING IT.

problem_benchmarks=("psb2_text" "humaneval_text")
models=("Gemma2B" "CodeGemma7B" "LLaMA318B" "CodeLLaMA7B" "Mistral7B" "Phi35Mini")

for problem_benchmark in ${problem_benchmarks[@]}
do
	cd ${problem_benchmark}
    for model in ${models[@]}
	do
		cd ${model}/iter10_rep0
        #rm -r train40_test1000
        #rm -r train60_test1000
        cp -r train20_test1000 train40_test1000
        cp -r train20_test1000 train60_test1000
        cd ../..
	done
    cd ..
done
