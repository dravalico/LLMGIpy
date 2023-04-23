from abc import ABC, abstractmethod


class AbstractLanguageModel(ABC):
    __NAME: str = ""

    def __init__(self, model_name: str):
        super().__init__()
        self._load_model()
        self.__NAME = model_name

    @abstractmethod
    def ask(self, question: str) -> any:
        pass

    @property
    def name(self) -> str:
        return self.__NAME

    @abstractmethod
    def _load_model(self) -> any:
        print("Loading model...")
        pass
