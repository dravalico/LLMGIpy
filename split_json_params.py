#!/usr/bin/env python3

import json
import os
from itertools import product
from pathlib import Path
import argparse


def expand_benchmarks(benchmarks, chunk_size=25):
    expanded = []
    for name, start, end, btype in benchmarks:
        for i in range(start, end + 1, chunk_size):
            new_end = min(i + chunk_size - 1, end)
            expanded.append([name, i, new_end, btype])
    return expanded


def main(json_path, results_dir, output_dir):
    with open(json_path, "r") as f:
        config = json.load(f)

    llm_params = config["llm_params"]
    pony_params = config["pony_params"]

    # Extract and expand
    model_names = llm_params["model_names"]
    benchmark_names = expand_benchmarks(llm_params["benchmark_names"])
    iterations = llm_params["iterations"]
    train_sizes = llm_params["train_sizes"]
    test_sizes = llm_params["test_sizes"]
    dynamic_bnf = llm_params["dynamic_bnf"]

    # Cartesian product
    combinations = list(product(model_names, benchmark_names, iterations, train_sizes, test_sizes, dynamic_bnf))

    # Ensure output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create files and parallel command list
    parallel_lines = []
    for i, (model, bench, it, train, test, bnf) in enumerate(combinations, start=1):
        new_json = {
            "llm_params": {
                "model_names": [model],
                "benchmark_names": [bench],
                "iterations": [it],
                "train_sizes": [train],
                "test_sizes": [test],
                "dynamic_bnf": [bnf]
            },
            "pony_params": pony_params
        }
        json_filename = os.path.join(output_dir, f"llm_input_{i}.json")
        with open(json_filename, "w") as f:
            json.dump(new_json, f, indent=4)

        output_txt = os.path.join(output_dir, f"llm_output_{i}.txt")
        parallel_lines.append(f"{json_filename};{results_dir};{output_txt}")

    # Save parallel input file
    parallel_txt_path = os.path.join(output_dir, "parallel_input.txt")
    with open(parallel_txt_path, "w") as f:
        f.write("\n".join(parallel_lines))


    print(f"Done. {len(combinations)} JSON files created in: {output_dir}")
    print(f"Commands saved to: {parallel_txt_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split LLM JSON configuration for parallel execution.")
    parser.add_argument("--json", required=True, help="Path to the input JSON config.")
    parser.add_argument("--results_dir", required=True, help="Path to the results directory.")
    parser.add_argument("--output_dir", required=True, help="Directory to store output JSON and scripts.")

    args = parser.parse_args()
    main(args.json, args.results_dir, args.output_dir)

