#!/bin/bash

# remove the corresponding _complete_dynamic.bnf file before running this

python3 llmpony/pony/scripts/GE_LR_parser.py --reverse_mapping_target "${1}" --grammar_file "${2}"
