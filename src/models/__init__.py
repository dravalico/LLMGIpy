ALL_LLMs: dict[str, tuple[str, str]] = {
    'Gemma2B': ('HuggingFaceLLM', 'google/gemma-1.1-2b-it'),
    'Gemma7B': ('HuggingFaceLLM', 'google/gemma-1.1-7b-it'),
    'CodeGemma7B': ('HuggingFaceLLM', 'google/codegemma-7b-it'),
    'LLaMA27B': ('HuggingFaceLLM', 'meta-llama/Llama-2-7b-chat-hf'),
    'LLaMA213B': ('HuggingFaceLLM', 'meta-llama/Llama-2-13b-chat-hf'),
    'LLaMA38B': ('HuggingFaceLLM', 'meta-llama/Meta-Llama-3-8B-Instruct'),
    'CodeLLaMA7B': ('HuggingFaceLLM', 'meta-llama/CodeLlama-7b-Instruct-hf'),
    'CodeLLaMA13B': ('HuggingFaceLLM', 'meta-llama/CodeLlama-13b-Instruct-hf'),
    'StarCoder3B': ('HuggingFaceLLM', 'bigcode/starcoder2-3b'),
    'StarCoder7B': ('HuggingFaceLLM', 'bigcode/starcoder2-7b'),
    'Mistral7B': ('HuggingFaceLLM', 'mistralai/Mistral-7B-Instruct-v0.2'),
    'ChatGPT': ('OpenAILLM', 'gpt-3.5-turbo'),
    'GPT4': ('OpenAILLM', 'gpt-4'),
}

models_list = sorted([key for key in ALL_LLMs])