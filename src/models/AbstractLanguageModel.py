from abc import ABC, abstractmethod
from typing import Any
from models import ALL_LLMs


class AbstractLanguageModel(ABC):
    _INTRODUCTION_TO_QUESTION: dict[str, str] = {
        'psb2': 'Write a single Python function to solve the following problem and insert the necessary modules:\n',
        'humaneval': 'Complete the following Python function based on the provided comment and insert the necessary modules:\n'
    }

    def __init__(self, model_name: str, problem_bench: str) -> None:
        super().__init__()
        self.__NAME = model_name.strip()
        self._problem_bench = problem_bench.strip()

        allowed_models: list[str] = [key for key in ALL_LLMs if ALL_LLMs[key][0] == self.__class__.__name__]

        if self.name.lower() not in [n_model.lower() for n_model in allowed_models]:
            raise AttributeError(
                f'Cannot recognize llm {self.name} for category {self.__class__.__name__}. It is not in the dictionary of known llms, which are: {str(allowed_models)}.')

        self.__llm_id: str = ALL_LLMs[self.name][1]
        self._load_model()

    def problem_bench(self) -> str:
        return self._problem_bench

    def llm_id(self) -> str:
        return self.__llm_id
    
    @abstractmethod
    def get_complete_prompt(self, prompt: str, reask: bool) -> str:
        pass

    @abstractmethod
    def ask(self, prompt: str, reask: bool) -> str:
        pass

    @property
    def name(self) -> str:
        return self.__NAME

    @abstractmethod
    def _load_model(self) -> Any:
        print("Loading model...")
        pass
