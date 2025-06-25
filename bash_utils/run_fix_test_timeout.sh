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
python3 fix_test_timeout.py --run_id ${1} --parameters ${2} ${verbose_param}
end=$(date +%s)
