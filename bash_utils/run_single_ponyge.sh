#!/bin/bash

cd PonyGE2/src

start=$(date +%s)
python3 ponyge.py --parameters ${1}
end=$(date +%s)
echo "${1} $(( end - start ))" >> ../../bash_utils/timings_ponyge.txt
