from abc import ABC, abstractmethod
from typing import Any


class AbstractLanguageModel(ABC):
    _INTRODUCTION_TO_QUESTION: str = "Write a single Python function to solve the following problem inserting the "\
                                      "necessary modules: "
    
    def __init__(self, model_name: str) -> None:
        super().__init__()
        self.__NAME = model_name
        self._load_model()

    @abstractmethod
    def ask(self, question: str, reask: bool) -> str:
        pass

    @property
    def name(self) -> str:
        return self.__NAME

    @abstractmethod
    def _load_model(self) -> Any:
        print("Loading model...")
        pass
