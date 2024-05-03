from abc import ABC, abstractmethod
from typing import Any


class AbstractLanguageModel(ABC):
    _INTRODUCTION_TO_QUESTION: dict[str, str] = {
        'psb2': 'Write a single Python function to solve the following problem inserting the necessary modules: ',
        'humaneval': 'Complete the following Python function based on the provided comment: '
    }
    
    def __init__(self, model_name: str, problem_bench: str) -> None:
        super().__init__()
        self.__NAME = model_name
        self._problem_bench = problem_bench

    def problem_bench(self) -> str:
        return self._problem_bench

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
