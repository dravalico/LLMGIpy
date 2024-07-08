#!/bin/bash

parallel --jobs ${2} --colsep ',' --ungroup ./bash_utils/run_fix_test_timeout.sh {1} :::: ${1}
