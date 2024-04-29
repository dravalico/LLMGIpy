from typing import Any
from models.AbstractLanguageModel import AbstractLanguageModel
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os


class Gemma2B(AbstractLanguageModel):
    __FIRST_PART: str = '<bos><start_of_turn>user\n'
    __SECOND_PART: str = '<end_of_turn>\n<start_of_turn>model\n'

    def __init__(self, problem_bench: str) -> None:
        super().__init__("Gemma2B", problem_bench)

    def ask(self, prompt: str, reask: bool) -> str:
        if not reask:
            prompt: str = (
                self.__FIRST_PART
                + self._INTRODUCTION_TO_QUESTION[self.problem_bench()]
                + prompt
                + self.__SECOND_PART
            )
        else:
            prompt: str = (
                self.__FIRST_PART
                + prompt
                + self.__SECOND_PART
            )
        input_ids = self.__tokenizer(prompt, return_tensors="pt").to("cuda")

        outputs = self.__model.generate(**input_ids)
        result = self.__tokenizer.decode(outputs[0])
        return self.__extract_response(result)

    def _load_model(self) -> Any:
        super()._load_model()
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)

        self.__tokenizer = AutoTokenizer.from_pretrained("google/gemma-1.1-2b-it", token=os.getenv('HUGGING_TOKEN'))
        self.__model = AutoModelForCausalLM.from_pretrained(
            "google/gemma-1.1-2b-it",
            token=os.getenv('HUGGING_TOKEN'),
            quantization_config=quantization_config
        )

    @staticmethod
    def __extract_response(response: str) -> str:
        return response[response.index(Gemma2B.__SECOND_PART) + len(Gemma2B.__SECOND_PART): len(response):]
