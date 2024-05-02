from peft import PeftModel
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from models.AbstractLanguageModel import AbstractLanguageModel


class Alpaca7B(AbstractLanguageModel):
    __ALPACA_QUESTION_FIRST_PART: str = "Below is an instruction that describes a task. Write a response that "\
                                        "appropriately completes the request.\n\n### Instruction:\n"
    __ALPACA_QUESTION_SECOND_PART: str = "\n\n### Response:\n"

    def __init__(self, problem_bench: str) -> None:
        super().__init__('Alpaca7B', problem_bench)

    def ask(self, prompt: str, reask: bool) -> str:
        if not reask:
            prompt: str = (
                self.__ALPACA_QUESTION_FIRST_PART
                + self._INTRODUCTION_TO_QUESTION[self.problem_bench()]
                + prompt
                + self.__ALPACA_QUESTION_SECOND_PART
            )
        else:
            prompt: str = (
                self.__ALPACA_QUESTION_FIRST_PART
                + prompt
                + self.__ALPACA_QUESTION_SECOND_PART
            )
        inputs = self.__tokenizer(
            prompt,
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

    def _load_model(self) -> None:
        super()._load_model()
        self.__tokenizer = AutoTokenizer.from_pretrained(
            "decapoda-research/llama-7b-hf"
        )
        self.__model = AutoModelForCausalLM.from_pretrained(
            "decapoda-research/llama-7b-hf",
            load_in_8bit=True,
            device_map="auto",
        )
        self.__model = PeftModel.from_pretrained(self.__model, "samwit/alpaca7B-lora")

    @staticmethod
    def __extract_response(alpaca_response: str) -> str:
        return alpaca_response[alpaca_response.index("### Response") + len("### Response:\n"): len(alpaca_response):]
