import re
from typing import Any
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os
from llmpony.llm.models import ALL_LLMs


class GrammarGeneratorLLM:
    def __init__(self, model_name: str = "LLaMA38B_G", grammar_task: str = "generate_grammar") -> None:
        """
        Initializes a GrammarGeneratorLLM object with the given model name and grammar task.
        
        Args:
            model_name (str, optional): The name of the model to use. Defaults to "LLaMA38B_G".
            grammar_task (str, optional): The task to perform with the grammar. Defaults to "generate_grammar".
        
        Returns:
            None
        
        Raises:
            AttributeError: If the given model name is not recognized.
        """
        self.__PROMPT_GRAMMAR_TEMPLATE: dict[str, str] = {
        'generate_grammar': 'Given this bnf grammar:\n{bnf}\n i want that you write a smaller grammar for encode this code:\n{code}\n\n',
        'generate_grammar_from_zero': 'I have this problem:\n{prompt}\nAnd this code is the solution for the problem:\n{code}\n\nI want you to write the bnf grammar for the problem:\n',
        'find_tags_grammar': 'I have this problem:\n{prompt}\nAnd this code is the "solution" for the problem:\n{code}\n\nI also have this bnf grammar:\n{bnf}\nI want you to find all the tags in the bnf grammar for encode the code:\n',
        }
        self.__NAME = model_name
        self._grammar_task = grammar_task
        self._prompt_template = self.__PROMPT_GRAMMAR_TEMPLATE[grammar_task]
        self._bnf_content = None
        allowed_models: list[str] = [key for key in ALL_LLMs if ALL_LLMs[key][0] == self.__class__.__name__]

        if self.name.lower() not in [n_model.lower() for n_model in allowed_models]:
            raise AttributeError(
                f'Cannot recognize llm {self.name} for category {self.__class__.__name__}. It is not in the dictionary of known llms, which are: {str(allowed_models)}.')

        self.__llm_id: str = ALL_LLMs[self.name][1]
        self._load_model()
        
    def print_prompt_grammar_template(self, keywords: list[str]):
        for k in keywords:
            print(f"The grammar template for {k} is: {self.__PROMPT_GRAMMAR_TEMPLATE[k].__str__()}")
            
    def print_prompt_keywords(self):
        print(self.__PROMPT_GRAMMAR_TEMPLATE.keys())
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} -> (name={self.name}, llm_id={self.llm_id()}, task={self._grammar_task}, bnf_content={self._bnf_content})"
    
    def __str__(self) -> str:
        return f"The model name is {self.name} and the exact HF model id is {self.llm_id()}\nThe actual task is {self._grammar_task}"
        
    def llm_id(self) -> str:
        return self.__llm_id
    
    @property
    def name(self) -> str:
        return self.__NAME
    
    def read_grammar_file(self, grammar_path: str):
        with open(grammar_path, 'r') as file:
                self._bnf_content = file.read() 

    def get_complete_prompt(self, prompt: str, code: str, grammar_str: str = None) -> str:
        """
        Generates a complete prompt for the BNF generation task.

        Args:
            prompt (str): The prompt for the BNF generation task.
            code (str): The code for the BNF generation task.
            grammar_str (str, optional): The BNF grammar string. Defaults to None.

        Returns:
            str: The complete prompt for the BNF generation task.

        This function generates a complete prompt for the BNF generation task based on the provided prompt, code, and grammar string.
        If the grammar task is set to 'generate_grammar_from_zero', the prompt is formatted with the given prompt and code.
        Otherwise, the prompt is formatted with the given grammar string, prompt, and code.
        """
        if self._grammar_task == 'generate_grammar_from_zero':
            bnf_generation_prompt = self._prompt_template.format(prompt = prompt, code = code)
        else:
            bnf_generation_prompt = self._prompt_template.format(bnf = grammar_str, prompt = prompt, code = code)
        return bnf_generation_prompt

    def ask(self, prompt: str, code: str, grammar_path: str = None) -> str:
        """
        Generates a response based on the given prompt, code, and grammar path.

        Args:
            prompt (str): The prompt for the BNF generation task.
            code (str): The code for the BNF generation task.
            grammar_path (str, optional): The path to the grammar file. Defaults to None.

        Returns:
            str: The generated response.

        This function generates a response based on the given prompt, code, and grammar path. It first reads the grammar
        file if a path is provided, otherwise it uses the pre-loaded BNF content. It then formats the prompt using the
        grammar string, prompt, and code. It creates a chat template with the formatted prompt and applies it to the
        tokenizer. It generates the input IDs and sets the terminators. It then generates the response using the model
        and decodes it using the tokenizer. The function returns the decoded response.
        """
        grammar_str = self.read_grammar_file(grammar_path) if grammar_path is not None else self._bnf_content
        prompt = self.get_complete_prompt(prompt, code, grammar_str=grammar_str)

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
    
    def ask_just_grammar(self, prompt: str, code: str, grammar_path: str = None) -> str:
        raw_response = self.ask(prompt, code, grammar_path)
        pattern = r'```(.*?)```'
        return re.findall(pattern, raw_response, re.DOTALL)[0]
        
        

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
