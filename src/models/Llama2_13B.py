from ctransformers import AutoModelForCausalLM, AutoTokenizer
from transformers import pipeline
from models.AbstractLanguageModel import AbstractLanguageModel


class Llama2_13B(AbstractLanguageModel):
    __LLAMA2_QUESTION_FIRST_PART: str = "Below is an instruction that describes a task. Write a response that "\
                                        "appropriately completes the request.\n\nQuestion:\n"
    __LLAMA2_QUESTION_SECOND_PART: str = "\n\nAnswer:\n"

    def __init__(self) -> None:
        super().__init__("Llama2_13B")

    def ask(self, question: str) -> str:
        question: str = (
            self.__LLAMA2_QUESTION_FIRST_PART
            + self._INTRODUCTION_TO_QUESTION
            + question
            + self.__LLAMA2_QUESTION_SECOND_PART
        )
        inputs = self.__tokenizer(
            question,
            return_tensors="pt",
        )
        input_ids = inputs["input_ids"]
        generation_output = self.__model.generate(
            input_ids=input_ids,
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=256,
        )
        result: str = ""
        for s in generation_output.sequences:
            result = result + self.__tokenizer.decode(s)
        print(result)
        print("="*40)
        print(self.__extract_response(result))
        print("="*40)
        return self.__extract_response(result)

    def _load_model(self) -> None:
        super()._load_model()
        #self.__model = AutoModelForCausalLM.from_pretrained("TheBloke/Llama-2-13B-chat-GGUF", model_file="llama-2-13b-chat.Q5_K_M.gguf",
        #                                                    hf=True,  gpu_layers=0)
        self.__model  = AutoModelForCausalLM.from_pretrained("TheBloke/Llama-2-13B-GGUF", model_file="llama-2-13b.Q6_K.gguf",
                                                           model_type="llama", gpu_layers=0, hf=True)
        self.__tokenizer = AutoTokenizer.from_pretrained(self.__model)

    @staticmethod
    def __extract_response(llama2_response: str) -> str:
        return llama2_response[llama2_response.index("Answer:") + len("Answer:\n"): len(llama2_response):]
