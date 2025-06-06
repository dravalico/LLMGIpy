#!/bin/bash

cd llmpony/pony

python3 scripts/GE_LR_parser.py --reverse_mapping_target "${1}" --grammar_file "${2}"
