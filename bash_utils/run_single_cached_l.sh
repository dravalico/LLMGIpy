#!/bin/bash

cd src

if [ -z ${4} ]
then
      problem_indexes_param=""
else
      problem_indexes_param="--problems_indexes ${5}"
fi

start=$(date +%s)
python3 main.py --model ${1} --dataset ${2} --prompt_type "text" --train_size ${3} --target_train_size ${4} --iterations 10 ${problem_indexes_param}
end=$(date +%s)
