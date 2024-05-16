#!/bin/bash

if [[ "$#" != "1" ]]; then
    echo "Usage ./check.sh relative_path"
    exit 1
fi

for e in $(ls $1 | grep '.json'); do
    is_exc=$(cat "$1/$e" | grep '"exception": "Traceback')
    if [[ -n $is_exc ]]; then
        echo "$e        (Exception)"
    fi
    is_exc=$(cat "$1/$e" | grep '"error": "Process timed out"')
    if [[ -n $is_exc ]]; then
        echo "$e        (Process timed out)"
    fi
done
