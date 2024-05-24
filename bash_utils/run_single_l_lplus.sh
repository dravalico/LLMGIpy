#!/bin/bash

cd src

if [ -z ${4} ]
then
      problem_indexes_param=""
else
      problem_indexes_param="--problem_indexes ${4}"
fi

start=$(date +%s)
python3 main.py --model ${1} --dataset ${2} --train_size ${3}  --iterations 10 ${problem_indexes_param}
end=$(date +%s)
start=$(date +%s)
python3 main.py --model ${1} --dataset ${2} --train_size ${3}  --iterations 10 --repeatitions 10 --reask ${problem_indexes_param}
end=$(date +%s)
