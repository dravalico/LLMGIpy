![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

# LLMGIpy

Large Language Model Genetic Improvement Python (LLMGIpy) is a software that allows you to evaluate the Python code generation of some LLMs (for now Alpaca) and (in the future) test the improvements of the code after applying Genetic Improvement.

## Install dependencies

Currently LLMGIpy only supports Alpaca with the psb2 dataset; the ```llmgipy-example.py``` file currently uses the above model and runs tests only on the psb2 dataset.

It is recommended to use a conda environment in which python version 3.9 is installed
```
pip install python=3.9
```

To run LLMGIpy using the "Alpaca" large language model, you need to install the following packages
```
pip install datasets
pip install loralib
pip install sentencepiece
pip install git+https://github.com/zphang/transformers@c3dc391
pip install git+https://github.com/huggingface/peft.git
pip install bitsandbytes
```

Also, to have the psb2 dataset available, run the following command
```
pip install psb2
```

## Example

After cloning the repository, run
```
cd src
python llmgipy-example.py
```