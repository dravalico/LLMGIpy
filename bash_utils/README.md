# Bash script to help execution of experiments

`run_exp_l_lplus.sh` and `run_single_l_lplus.sh` must be runned from the root folder, i.e., `LLMGIpy`, after the repository has been cloned, run:

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

