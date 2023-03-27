from typing import Callable
from peft import PeftModel
from transformers import LLaMATokenizer, LLaMAForCausalLM, GenerationConfig
import AbstractLanguageModel


class AlpacaModel(AbstractLanguageModel.AbstractLanguageModel):
    __ALPACA_QUESTION_FIRST_PART: str = "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\nWrite a single python function to solve the following problem: "
    __ALPACA_QUESTION_SECOND_PART: str = "\n\n### Response:\n"
    __tokenizer = None
    __model = None

    def __init__(self):
        super().__init__()

    def _load_model(self) -> None:
        super()._load_model()
        self.__tokenizer = LLaMATokenizer.from_pretrained(
            "decapoda-research/llama-7b-hf"
        )
        model = LLaMAForCausalLM.from_pretrained(
            "decapoda-research/llama-7b-hf",
            load_in_8bit=True,
            device_map="auto",
        )
        self.__model = PeftModel.from_pretrained(model, "samwit/alpaca7B-lora")

    def ask(self, question: str) -> str:
        super().ask(question)
        question = (
            self.__ALPACA_QUESTION_FIRST_PART
            + question
            + self.__ALPACA_QUESTION_SECOND_PART
        )
        inputs = self.__tokenizer(
            question,
            return_tensors="pt",
        )
        input_ids = inputs["input_ids"].cuda()
        generation_config = GenerationConfig(
            temperature=0.6,
            top_p=0.95,
            repetition_penalty=1.2,
        )
        generation_output = self.__model.generate(
            input_ids=input_ids,
            generation_config=generation_config,
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=256,
        )
        result: str = ""
        for s in generation_output.sequences:
            result = result + self.__tokenizer.decode(s)
        return self.__extract_response(result)

    def __extract_response(self, alpaca_response: str) -> str:
        return alpaca_response[
            alpaca_response.index("### Response")
            + len("### Response:\n") : len(alpaca_response) :
        ]
