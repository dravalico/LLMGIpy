#!/bin/bash

if [ -z ${3} ]
then
      verbose_param=""
else
      if [ "${3}" = "-v" ]
      then
            verbose_param="--verbose"
      else
            verbose_param="" 
      fi
fi

start=$(date +%s)
python3 ponyge.py --run_id ${1} --parameters ${2} ${verbose_param}
end=$(date +%s)
echo "${2} $(( end - start ))" >> bash_utils/timings_ponyge.txt
