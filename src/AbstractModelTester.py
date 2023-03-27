from abc import ABC, abstractmethod


class AbstractModelTester(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def run(self) -> any:
        pass