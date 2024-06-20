#!/bin/bash

cd PonyGE2/src

if [ -z ${2} ]
then
      verbose_param=""
else
      if [ "${2}" = "-v" ]
      then
            verbose_param="--verbose"
      else
            verbose_param="" 
      fi
fi

start=$(date +%s)
python3 ponyge.py --parameters ${1} ${verbose_param}
end=$(date +%s)
echo "${1} $(( end - start ))" >> ../../bash_utils/timings_ponyge.txt
