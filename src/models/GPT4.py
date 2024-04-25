import os
import openai
from models.AbstractLanguageModel import AbstractLanguageModel


class GPT4(AbstractLanguageModel):
    def __init__(self, problem_bench: str) -> None:
        super().__init__("GPT4", problem_bench)

    def ask(self, prompt: str, reask: bool) -> str:
        if not reask:
            prompt = self._INTRODUCTION_TO_QUESTION[self.problem_bench()] + prompt
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content

    def _load_model(self) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
