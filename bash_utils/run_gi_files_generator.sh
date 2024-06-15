#!/bin/bash

cd src

if [ -z ${3} ]
then
      output_path=""
else
      output_path="--input_params_ponyge ${3}"
fi

start=$(date +%s)
python3 generate_impr_grammars_seeds_files.py --json_params ${1} --results_dir ${2} ${output_path}
end=$(date +%s)
