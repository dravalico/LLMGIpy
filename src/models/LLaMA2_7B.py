from transformers import AutoTokenizer
import transformers
import torch
from models.AbstractLanguageModel import AbstractLanguageModel
import re


class LLaMA2_7B(AbstractLanguageModel):

    def __init__(self) -> None:
        super().__init__("LLaMA2_7B")

    def ask(self, question: str) -> str:
        question: str = ("Results: " + question + "\nAnswer:")
        sequences = self.__pipeline(
            question,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=self.__tokenizer.eos_token_id,
            max_length=200,
        )
        result: str = ""
        print("=====")
        for seq in sequences:
            print(seq['generated_text'])
            result += seq['generated_text']
        print("=====")
        #print(self.__extract_response(result))
        return self.__extract_response(result)

    def _load_model(self) -> None:
        super()._load_model()
        model = "meta-llama/Llama-2-7b-hf"
        self.__tokenizer = AutoTokenizer.from_pretrained(model, use_auth_token=True)
        self.__pipeline = transformers.pipeline(
            "text-generation",
            model=model,
            torch_dtype=torch.float16,
            device_map="auto",
        )

    @staticmethod
    def __extract_response(alpaca_response: str) -> str:
        code_blocks = re.findall(r'begin{code}(.*?)end{code}', alpaca_response, re.DOTALL)
        extracted_code = '\n'.join(code_blocks)
        return extracted_code