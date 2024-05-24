ALL_LLMs: dict[str, tuple[str, str]] = {
    'Gemma2B': ('HuggingFaceLLM', 'google/gemma-1.1-2b-it', 'assistant'),
    'Gemma7B': ('HuggingFaceLLM', 'google/gemma-1.1-7b-it', 'assistant'),
    'CodeGemma7B': ('HuggingFaceLLM', 'google/codegemma-7b-it', 'assistant'),
    'LLaMA27B': ('HuggingFaceLLM', 'meta-llama/Llama-2-7b-chat-hf', 'assistant'),
    'LLaMA213B': ('HuggingFaceLLM', 'meta-llama/Llama-2-13b-chat-hf', 'assistant'),
    'LLaMA38B': ('HuggingFaceLLM', 'meta-llama/Meta-Llama-3-8B-Instruct', 'assistant'),
    'CodeLLaMA7B': ('HuggingFaceLLM', 'meta-llama/CodeLlama-7b-Instruct-hf', 'assistant'),
    'CodeLLaMA13B': ('HuggingFaceLLM', 'meta-llama/CodeLlama-13b-Instruct-hf', 'assistant'),
    'Mistral7B': ('HuggingFaceLLM', 'mistralai/Mistral-7B-Instruct-v0.2', 'assistant'),
    'ChatGPT': ('OpenAILLM', 'gpt-3.5-turbo', 'assistant'),
    'GPT4': ('OpenAILLM', 'gpt-4', 'assistant'),
    'LLaMA38B_G': ('GrammarGeneratorLLM', 'meta-llama/Meta-Llama-3-8B-Instruct', 'assistant'),
}

models_list = sorted([key for key in ALL_LLMs])
all_llms_macro_categories = sorted(list(set([ALL_LLMs[key][0] for key in ALL_LLMs])))