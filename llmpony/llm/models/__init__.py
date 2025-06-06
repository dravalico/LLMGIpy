ALL_LLMs: dict[str, tuple[str, str]] = {
    'Gemma2B': ('HuggingFaceLLM', 'google/gemma-1.1-2b-it', 'assistant'),
    'Gemma7B': ('HuggingFaceLLM', 'google/gemma-1.1-7b-it', 'assistant'),
    'CodeGemma7B': ('HuggingFaceLLM', 'google/codegemma-7b-it', 'assistant'),
    'LLaMA27B': ('HuggingFaceLLM', 'meta-llama/Llama-2-7b-chat-hf', 'assistant'),
    'LLaMA213B': ('HuggingFaceLLM', 'meta-llama/Llama-2-13b-chat-hf', 'assistant'),
    'LLaMA38B': ('HuggingFaceLLM', 'meta-llama/Meta-Llama-3-8B-Instruct', 'assistant'),
    'LLaMA318B': ('HuggingFaceLLM', 'meta-llama/Meta-Llama-3.1-8B-Instruct', 'assistant'),
    'LLaMA323B': ('HuggingFaceLLM', 'meta-llama/Llama-3.2-3B-Instruct', 'assistant'),
    'LLaMA321B': ('HuggingFaceLLM', 'meta-llama/Llama-3.2-1B-Instruct', 'assistant'),
    'LLaMA3211B': ('HuggingFaceLLM', 'meta-llama/Llama-3.2-11B-Vision-Instruct', 'assistant'),
    'CodeLLaMA7B': ('HuggingFaceLLM', 'meta-llama/CodeLlama-7b-Instruct-hf', 'assistant'),
    'CodeLLaMA13B': ('HuggingFaceLLM', 'meta-llama/CodeLlama-13b-Instruct-hf', 'assistant'),
    'Mistral7B': ('HuggingFaceLLM', 'mistralai/Mistral-7B-Instruct-v0.2', 'assistant'),
    'Phi35Mini': ('HuggingFaceLLM', 'microsoft/Phi-3.5-mini-instruct', 'assistant'),
    'Phi4Mini': ('HuggingFaceLLM', 'microsoft/Phi-4-mini-instruct', 'assistant'),
    'DeepSeekMini': ('HuggingFaceLLM', 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B', 'assistant'),
    'Yi9B': ('HuggingFaceLLM', '01-ai/Yi-1.5-9B-Chat', 'assistant'),
    'Yi1B': ('HuggingFaceLLM', '01-ai/Yi-Coder-1.5B-Chat', 'assistant'),
    'ChatGPT': ('OpenAILLM', 'gpt-3.5-turbo', 'assistant'),
    'GPT4': ('OpenAILLM', 'gpt-4', 'assistant'),
    'LLaMA38B_G': ('GrammarGeneratorLLM', 'meta-llama/Meta-Llama-3-8B-Instruct', 'assistant'),
}

models_list = sorted([key for key in ALL_LLMs])
all_llms_macro_categories = sorted(list(set([ALL_LLMs[key][0] for key in ALL_LLMs])))
