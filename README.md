![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

# LLMGIpy

Large Language Model Genetic Improvement Python (LLMGIpy) is a software that allows you to evaluate the Python code generation of some LLMs and test the improvements of the code after applying Genetic Improvement.

## Included LLMs

- Gemma1.1 2B and 7B
- LLaMA2 7B and 13B
- LLaMA3 8B
- CodeLLaMA 7B and 13B
- CodeGemma 7B
- Mistal 7B

## Setup

To clone this repository, you need to have `git` installed. After that you can open a terminal window and run

```
git clone https://github.com/dravalico/LLMGIpy.git
```

Move to the project folder

```
cd LLMGIpy
```

Now you need to install the dependencies. Make sure you have `pip` installed and then run

```
pip3 install -r requirements.txt
```

To run the program, do the following

```
cd src
```

and finally, you can run the helper to know the parameters you can use

```
python3 main.py --help
```
