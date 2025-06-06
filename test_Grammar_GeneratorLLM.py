from llmpony.llm.models.GrammarGeneratorLLM import GrammarGeneratorLLM
from dotenv import load_dotenv


load_dotenv()


print("Start test GrammarGeneratorLLM")
GrammarGLM = GrammarGeneratorLLM(model_name="LLaMA38B_G", grammar_task="generate_grammar_from_zero")

print("Grammar template")
print(GrammarGLM.print_prompt_grammar_template(['generate_grammar_from_zero']))
print("="*30)
print("Keywords")
print(GrammarGLM.print_prompt_keywords())
print("="*30)
print("print")
print(GrammarGLM)
print("="*30)
print("Llm_id")
print(GrammarGLM.llm_id())
print("="*30)
print("get complete prompt")
print(GrammarGLM.get_complete_prompt(prompt="!!!test_prompt!!!", code="!!!test_code!!!"))
print("="*30)
print("ask to the model")
model_response = GrammarGLM.ask(prompt="Create a fibonacci python function", code="def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)")
print("="*30)
print("model_response")
print(model_response)
print(GrammarGLM.get_complete_prompt(prompt="Create a fibonacci python function", code="def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"))
print("="*30)
print("="*30)
print("Finish")
