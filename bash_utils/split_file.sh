#!/bin/bash

file="${1}"
k=${2}  # number of parts

n=$(wc -l < "$file")
lines_per_file=$((n / k))
remainder=$((n % k))

start=1
for ((i=1; i<=k; i++)); do
    extra=0
    if (( i == k )); then
        # Last file: take the remainder into account
        extra=$remainder
    fi

    end=$((start + lines_per_file + extra - 1))
    output_file="split_${i}.txt"
    
    # Extract lines and prepend filename prefix
    sed -n "${start},${end}p" "$file" | awk -v prefix="$output_file;" '{print prefix $0}' > "$output_file"

    start=$((end + 1))
done

