#!/bin/bash

if [ -z "${timestamp_ponyge}" ]; then
    timestamp_ponyge=$(date +"%Y-%m-%dT%T")
fi

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
python3 ponyge.py --parameters ${1} --timestamp_ponyge ${timestamp_ponyge} ${verbose_param}
end=$(date +%s)
echo "${1} $(( end - start ))" >> bash_utils/timings_ponyge.txt
