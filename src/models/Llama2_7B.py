from transformers import AutoTokenizer
import transformers
import torch
from models.AbstractLanguageModel import AbstractLanguageModel
import os


class Llama2_7B(AbstractLanguageModel):

    def __init__(self) -> None:
        super().__init__("Llama2_7B")

    def ask(self, question: str) -> str:
        question: str = (self._INTRODUCTION_TO_QUESTION + question)
        sequences = self.__pipeline(
            question,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=self.__tokenizer.eos_token_id,
            max_length=200,
        )
        result: str = ""
        for seq in sequences:
            result += seq['generated_text']
        return result

    def _load_model(self) -> None:
        super()._load_model()
        model = "meta-llama/Llama-2-7b-hf"
        self.__tokenizer = AutoTokenizer.from_pretrained(model, token=os.getenv("HF_TOKEN"), use_auth_token=True)
        self.__pipeline = transformers.pipeline(
            "text-generation",
            model=model,
            torch_dtype=torch.float16,
            device_map="auto",
        )
