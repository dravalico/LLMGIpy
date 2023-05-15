from abc import ABC, abstractmethod


class AbstractLanguageModel(ABC):
    _INTRODUCTION_TO_QUESTION: str = "Write a single Python function to solve the following problem inserting the "\
                                      "necessary modules: "
    
    def __init__(self, model_name: str) -> None:
        super().__init__()
        self.__NAME = model_name
        self._load_model()

    @abstractmethod
    def ask(self, question: str) -> str:
        pass

    @property
    def name(self) -> str:
        return self.__NAME

    @abstractmethod
    def _load_model(self) -> any:
        print("Loading model...")
        pass
