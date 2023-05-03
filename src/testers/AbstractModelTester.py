from abc import ABC, abstractmethod
from models.AbstractLanguageModel import AbstractLanguageModel


class AbstractModelTester(ABC):

    def __init__(self, model: AbstractLanguageModel):
        super().__init__()
        if not isinstance(model, AbstractLanguageModel):
            e: str = "You must provide an AbstractLanguageModel instance."
            raise Exception(e)

    @abstractmethod
    def run(self) -> any:
        pass

    @staticmethod
    def _extract_function_body(model_response: str) -> str:
        return model_response[model_response.index("def"): len(model_response):]

    @staticmethod
    def _extract_function_name(function_body: str) -> str:
        # function_name = regex.findall("\s*(def)\s(.*?)\([a-zA-z]*\)", extracted_function)
        return function_body[function_body.index("def ") + len("def "): function_body.index("(")]

    @staticmethod
    def _indentation_as_tab(function: str) -> str:
        function = function.replace("    ", '\t')
        return function.replace("  ", '\t')
