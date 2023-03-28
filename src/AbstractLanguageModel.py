from abc import ABC, abstractmethod


class AbstractLanguageModel(ABC):
    __MODEL_NAME: str = ""

    def __init__(self, model_name: str):
        super().__init__()
        self._load_model()
        self.__MODEL_NAME = model_name

    @abstractmethod
    def ask(self, question: str) -> any:
        pass

    @property
    def model_name(self) -> str:
        return self.__MODEL_NAME

    @abstractmethod
    def _load_model(self) -> any:
        print("Loading model...")
        pass
