from abc import ABC, abstractmethod
from typing import Any
from models import ALL_LLMs


class AbstractLanguageModel(ABC):
    _INTRODUCTION_TO_QUESTION: dict[str, dict[str, str]] = {
        'text': {
            'psb2': 'Write a single Python function to solve the following problem and insert the necessary modules:\n',
            'humaneval': 'Complete the following Python function based on the provided comment and insert the necessary modules:\n'
        }
    }

    def __init__(self, model_name: str, problem_bench: str, prompt_type: str) -> None:
        super().__init__()
        self.__NAME = model_name.strip()
        self._problem_bench = problem_bench.strip()
        self._prompt_type = prompt_type.strip()

        allowed_models: list[str] = [key for key in ALL_LLMs if ALL_LLMs[key][0] == self.__class__.__name__]

        if self.name.lower() not in [n_model.lower() for n_model in allowed_models]:
            raise AttributeError(
                f'Cannot recognize llm {self.name} for category {self.__class__.__name__}. It is not in the dictionary of known llms, which are: {str(allowed_models)}.')

        self.__llm_class: str = ALL_LLMs[self.name][0]
        self.__llm_id: str = ALL_LLMs[self.name][1]
        self.__llm_chat_role: str = ALL_LLMs[self.name][2]
        self._load_model()

    def get_complete_prompt(self, prompt: str, original: bool) -> str:
        if not original:
            return self._INTRODUCTION_TO_QUESTION[self.prompt_type()][self.problem_bench()] + prompt
        return prompt

    def build_chat_from_prompts(self, prompts: list[str]) -> list[dict[str, str]]:
        if len(prompts) == 0:
            return [{"role": "user", "content": ""}]
        if len(prompts) == 1:
            return [{"role": "user", "content": self.get_complete_prompt(prompts[0], False)}]
        chat: list[dict[str, str]] = []
        roles: tuple[str, str] = ("user", self.llm_chat_role())
        current_role_idx: int = 0
        isFirst: bool = True
        for prompt in prompts:
            chat.append({"role": roles[current_role_idx], "content": self.get_complete_prompt(prompt, not isFirst)})
            current_role_idx = 1 - current_role_idx
            isFirst = False
        return chat

    def problem_bench(self) -> str:
        return self._problem_bench
    
    def prompt_type(self) -> str:
        return self._prompt_type

    def llm_class(self) -> str:
        return self.__llm_class

    def llm_id(self) -> str:
        return self.__llm_id
    
    def llm_chat_role(self) -> str:
        return self.__llm_chat_role

    @abstractmethod
    def ask(self, prompts: list[str]) -> str:
        pass

    @property
    def name(self) -> str:
        return self.__NAME

    @abstractmethod
    def _load_model(self) -> Any:
        print("Loading model...")
        pass
