#!/bin/bash

if [ -z ${4} ]
then
      problem_indexes_param=""
else
      problem_indexes_param="--problems_indexes ${4}"
fi

start=$(date +%s)
python3 main_llm.py --model ${1} --dataset ${2} --prompt_type "text" --train_size ${3}  --iterations 10 --repeatitions 5 --reask ${problem_indexes_param}
end=$(date +%s)
