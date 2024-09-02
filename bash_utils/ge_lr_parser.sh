#!/bin/bash

cd PonyGE2/src

python3 scripts/GE_LR_parser.py --reverse_mapping_target "${1}" --grammar_file "${2}"
