from typing import Any
from models.AbstractLanguageModel import AbstractLanguageModel
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os


class HuggingFaceLLM(AbstractLanguageModel):
    def __init__(self, model_name: str, problem_bench: str) -> None:
        super().__init__(model_name, problem_bench)

    def get_complete_prompt(self, prompt: str, reask: bool) -> str:
        if not reask:
            prompt = self._INTRODUCTION_TO_QUESTION[self.problem_bench()] + prompt
        return prompt

    def ask(self, prompt: str, reask: bool) -> str:
        prompt = self.get_complete_prompt(prompt, reask)

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
            max_new_tokens=2000,
            eos_token_id=terminators
        )

        response = outputs[0][input_ids.shape[-1]:]
        return self.__tokenizer.decode(response, skip_special_tokens=True)

    def _load_model(self) -> Any:
        super()._load_model()
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)

        model_id = self.llm_id()

        self.__tokenizer = AutoTokenizer.from_pretrained(model_id, token=os.getenv('HUGGING_TOKEN'))
        self.__model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            token=os.getenv('HUGGING_TOKEN'),
            quantization_config=quantization_config
        )
