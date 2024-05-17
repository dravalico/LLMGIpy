#!/bin/bash

cd src

start=$(date +%s)
python3 main.py --model ${1} --dataset ${2} --train_size ${3}  --iterations 10
end=$(date +%s)
echo "${2} ${3} ${1} 0 $(( end - start ))" >> ../bash_utils/timings.txt
start=$(date +%s)
python3 main.py --model ${1} --dataset ${2} --train_size ${3}  --iterations 10 --repeatitions 10 --reask
end=$(date +%s)
echo "${2} ${3} ${1} 1 $(( end - start ))" >> ../bash_utils/timings.txt

