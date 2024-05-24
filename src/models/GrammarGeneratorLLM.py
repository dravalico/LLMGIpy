from typing import Any
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os
from models import ALL_LLMs


class GrammarGeneratorLLM:
    def __init__(self, model_name: str = "LLaMA38B", grammar_task: str = "generate_grammar") -> None:
        __PROMPT_GRAMMAR_TEMPLATE: dict[str, str] = {
        'generate_grammar': 'Given this bnf grammar: {bnf}\n i want that you write a smaller grammar for encode this code:\n{code}\n\n',
        'generate_grammar_from_zero': 'I have this problem:\n{prompt}\nAnd this code is the solution for the problem:\n{code}\n\nI want you to write the bnf grammar for the problem:\n',
        'find_tags_grammar': 'I have this problem:\n{prompt}\nAnd this code is the "solution" for the problem:\n{code}\n\nI also have this bnf grammar:\n{bnf}\nI want you to find all the tags in the bnf grammar for encode the code:\n',
        }
        self.__NAME = model_name
        self._grammar_task = grammar_task
        self._prompt_template = __PROMPT_GRAMMAR_TEMPLATE[grammar_task]
        allowed_models: list[str] = [key for key in ALL_LLMs if ALL_LLMs[key][0] == self.__class__.__name__]

        if self.name.lower() not in [n_model.lower() for n_model in allowed_models]:
            raise AttributeError(
                f'Cannot recognize llm {self.name} for category {self.__class__.__name__}. It is not in the dictionary of known llms, which are: {str(allowed_models)}.')

        self.__llm_id: str = ALL_LLMs[self.name][1]
        self._load_model()
        
    def llm_id(self) -> str:
        return self.__llm_id
    
    @property
    def name(self) -> str:
        return self.__NAME
    
    def read_grammar_file(self, grammar_path: str) -> str:
        pass

    def get_complete_prompt(self, prompt: str, code: str, grammar_str: str = None) -> str:
        if self._grammar_task == 'generate_grammar_from_zero':
            bnf_generation_prompt = self._prompt_template.format(prompt = prompt, code = code)
        else:
            bnf_generation_prompt = self._prompt_template.format(bnf = grammar_str, prompt = prompt, code = code)
        return bnf_generation_prompt

    def ask(self, prompt: str) -> str:
        prompt = self.get_complete_prompt(prompt)

        messages = [
            {"role": "user", "content": prompt}
        ]

        input_ids = self.__tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.__model.device)

        terminators = [
            self.__tokenizer.eos_token_id,
            self.__tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = self.__model.generate(
            input_ids,
            max_new_tokens=1024,
            eos_token_id=terminators
        )

        response = outputs[0][input_ids.shape[-1]:]
        return self.__tokenizer.decode(response, skip_special_tokens=True)

    def _load_model(self) -> Any:
        print("Loading model...")
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)

        model_id = self.llm_id()

        self.__tokenizer = AutoTokenizer.from_pretrained(model_id, token=os.getenv('HF_TOKEN'))
        self.__model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            token=os.getenv('HF_TOKEN'),
            quantization_config=quantization_config
        )
