![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

# LLMGIpy

Large Language Model Genetic Improvement Python (LLMGIpy) is a software that allows you to evaluate the Python code generation of some LLMs and test the improvements of the code after applying Genetic Improvement.

## Included LLMs

- Gemma1.1 2B and 7B
- LLaMA2 7B and 13B
- LLaMA3 8B
- CodeLLaMA 7B and 13B
- CodeGemma 7B
- Mistral 7B
- ChatGPT and GPT4

Note that for Hugging Face models you need a (free) token and for OpenAI models you need to pay.

## Usage

Clone this repository, move to the folder

```
git clone https://github.com/dravalico/LLMGIpy
cd LLMGIpy
```

Create two conda environments with Python 3.11. Activate each of them separately, and install in each of them one of the requirements file listed here.

Run the scripts in the 'bash_utils' folder.

Make sure that you have an environment variable with your HUGGING FACE TOKEN set so that Hugging Face models can use it to run the models (the environment variable must be called HF_TOKEN).

