# Bash script to help execution of experiments

`run_exp_l_lplus.sh` and `run_single_l_lplus.sh` must be runned from the root folder, i.e., `LLMGIpy`, after the repository has been cloned, run:

```
cd LLMGIpy
chmod +x bash_utils/run_exp_l_lplus.sh
./bash_utils/{script_name}.sh
```

## Scripts explanation

- `run_exp_l_lplus.sh` does not need any parameters, it just run all models with all benchmark suites and some train set dimensions (parameters free)
- `run_single_l_lplus.sh` must need 3 parameters, in order: `model`, `dataset`, `train-size`, e.g. `./bash_utils/run_single_l_lplus.sh Gemma2B humaneval 20`
- `check_errors.sh` finds results that raised *exceptions* or *time out* in a folder containing the `.json` files, e.g. `./bash_utils/check_errors.sh results/{folder_name}`
