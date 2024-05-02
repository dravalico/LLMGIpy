from ctransformers import AutoModelForCausalLM
from models.AbstractLanguageModel import AbstractLanguageModel
import re

class LLaMA2_13B(AbstractLanguageModel):

    def __init__(self) -> None:
        super().__init__("LLaMA2_13B")

    def ask(self, question: str) -> str:
        question: str = ("Question: "+ super()._INTRODUCTION_TO_QUESTION + question + "\nAnswer:")
        sequences = self.__llm(question)
        print("*"*50)
        print(sequences)
        print("*"*50)
        return self.__extract_response(sequences)

    def _load_model(self) -> None:
        super()._load_model()
        self.__llm  = AutoModelForCausalLM.from_pretrained("TheBloke/Llama-2-13B-chat-GGUF", model_file="llama-2-13b-chat.Q5_K_M.gguf",
                                                           model_type="llama", gpu_layers=0,
                                                            max_new_tokens=256, temperature=0.6,
                                                            repetition_penalty=1.2) # HACK cambiato max token (su alpaca è di 256) perchè altrimenti non completava le risposte
        #self.__llm  = AutoModelForCausalLM.from_pretrained("TheBloke/Llama-2-13B-GGUF", model_file="llama-2-13b.Q6_K.gguf",
        #                                                   model_type="llama", gpu_layers=0)

    @staticmethod
    def __extract_response(llama2_response: str) -> str:
        try:
            code_blocks = re.findall(r'```(.*?)```', llama2_response, re.DOTALL)
            #return llama2_response[llama2_response.index("```") + len("```\n"): len(llama2_response):]
            extracted_code = '\n'.join(code_blocks)
            return extracted_code
        except:
            return llama2_response[llama2_response.index("def"): len(llama2_response):]