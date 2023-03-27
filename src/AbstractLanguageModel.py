from abc import ABC, abstractmethod


class AbstractLanguageModel(ABC):
    def __init__(self):
        super().__init__()
        self._load_model()

    @abstractmethod
    def _load_model(self) -> any:
        print("Loading model...")
        pass

    @abstractmethod
    def ask(self, question: str) -> any:
        pass
