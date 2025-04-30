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
    sed -n "${start},${end}p" "$file" > "split_${i}.txt"
    start=$((end + 1))
done

