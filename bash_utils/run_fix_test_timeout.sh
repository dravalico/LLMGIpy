#!/bin/bash

cd PonyGE2/src

start=$(date +%s)
python3 fix_test_timeout.py --parameters ${1}
end=$(date +%s)
