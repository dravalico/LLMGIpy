# Bash script to help execution of experiments

bash scripts must be runned from the root folder, i.e., `LLMGIpy`, after the repository has been cloned, run:

```
cd LLMGIpy
chmod +x bash_utils/{script_name}.sh
./bash_utils/{script_name}.sh {eventual_params}
```

## Scripts explanation

- `run_exp_l_lplus.sh` does not need any parameters, it just run all models with all benchmark suites and some train set dimensions (parameters free)
- `run_exp_l.sh` does not need any parameters, it just run all models with all benchmark suites and some train set dimensions (parameters free, only L)
- `run_exp_lplus.sh` does not need any parameters, it just run all models with all benchmark suites and some train set dimensions (parameters free, only LPLUS, i.e., the reask)
- `run_single_l_lplus.sh` must need 3 parameters, in order: `model`, `dataset`, `train-size`, e.g. `./bash_utils/run_single_l_lplus.sh Gemma2B humaneval 20`. It also accepts a fourth optional parameter indicating the problems indexes to evaluate (if not provided, all problems of that benchmark suite are evaluated), e.g., `./bash_utils/run_single_l_lplus.sh Gemma2B humaneval 20 5..10` or `./bash_utils/run_single_l_lplus.sh Gemma2B humaneval 20 5,6,7,10` or `./bash_utils/run_single_l_lplus.sh Gemma2B humaneval 20 6`.
- `run_single_l.sh` must need 3 parameters, in order: `model`, `dataset`, `train-size`, e.g. `./bash_utils/run_single_l.sh Gemma2B humaneval 20`. It also accepts a fourth optional parameter indicating the problems indexes to evaluate (if not provided, all problems of that benchmark suite are evaluated), e.g., `./bash_utils/run_single_l.sh Gemma2B humaneval 20 5..10` or `./bash_utils/run_single_l.sh Gemma2B humaneval 20 5,6,7,10` or `./bash_utils/run_single_l.sh Gemma2B humaneval 20 6` (only L).
- `run_single_lplus.sh` must need 3 parameters, in order: `model`, `dataset`, `train-size`, e.g. `./bash_utils/run_single_lplus.sh Gemma2B humaneval 20`. It also accepts a fourth optional parameter indicating the problems indexes to evaluate (if not provided, all problems of that benchmark suite are evaluated), e.g., `./bash_utils/run_single_lplus.sh Gemma2B humaneval 20 5..10` or `./bash_utils/run_single_lplus.sh Gemma2B humaneval 20 5,6,7,10` or `./bash_utils/run_single_lplus.sh Gemma2B humaneval 20 6` (only LPLUS).
- `check_errors.sh` finds results that raised *exceptions* or *time out* in a folder containing the `.json` files, e.g. `./bash_utils/check_errors.sh results/{folder_name}`

Some notes on the `problems\_indexes` parameter that you can set as optional parameter in some of the aforementioned scripts. You have three possible ways of using this parameter (problems indexes always start from 0):

- Running a single problem by specifying its index (e.g., 5 runs problem with index 5, that is, the 6th problem of the dataset);
- Running a sequence of problems by specifying their indexes separated by comma (e.g., 5,7,9,10 runs problems with index 5, 7, 9, and 10, in this order);
- Running a range of problems by specifying a start index and an end index (both inclusive) separated by .. (e.g., 5..10 runs problems with index 5, 6, 7, 8, 9, and 10, in this order).


- `run_gi_files_generator.sh` needs two parameters, it runs the Python script that generates grammars, seeds, and improvement parameters files. The first parameter is the path to a .json file detailing the combinations of parameters to use. The second parameter is the path to the folder containing the results for the LLMs responses. It eventually generates a .txt file with all the paths to the improvement parameters file if the path of this .txt file is provided as third (optional) parameter.
- `run_gi_files_generator_only_impr.sh` needs two parameters, it runs the Python script that generates grammars, seeds, and improvement parameters files. The first parameter is the path to a .json file detailing the combinations of parameters to use. The second parameter is the path to the folder containing the results for the LLMs responses. It eventually generates a .txt file with all the paths to the improvement parameters file if the path of this .txt file is provided as third (optional) parameter. This requires that grammars and seeds have already been generated, and it generates only the improvement parameters files. and eventually the .txt with all the improvement parameters files paths.
- `run_single_ponyge.sh` needs one parameter, it runs a PonyGE2-based evolution and performs Genetic Improvement. The required parameter is the path to the ponyge parameters .txt file. This path must begin with the 'improvements' folder, which is located in PonyGE2/parameters/. For instance, improvements/GI/psb2/CodeLLaMA7B/progimpr\_fitness\_type\_train1000\_test1000/lexicase\_pop1000\_gen100\_cxsubtree0.8mutsubtree0.6/problem0_seed0.txt is an example of valid path. Optionally, you can provide as second parameter a flag '-v' to run the evolution in verbose mode.
- `run_parallel_ponyge.sh` needs one parameter when running from the terminal which is the path to .txt file in which each line contains a path to a parameters file for pony (the same type of path of the parameter for `run_single_ponyge.sh` script). This script will run all the ponyge evolutions in parallel by using the available cores, specifically, it will run `run_single_ponyge.sh` for each path specified in the .txt file pointed by the command-line parameter of `run_parallel_ponyge.sh`. You must have parallel library from GNU installed on your system. This is executed with no verbose.
