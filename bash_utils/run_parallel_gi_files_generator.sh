#!/bin/bash

parallel --jobs ${2} --colsep ';' --ungroup ./bash_utils/run_gi_files_generator.sh {1} {2} {3} :::: ${1}
