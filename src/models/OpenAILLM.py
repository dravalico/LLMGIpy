import os
import openai
from models.AbstractLanguageModel import AbstractLanguageModel


class OpenAILLM(AbstractLanguageModel):
    def __init__(self, model_name: str, problem_bench: str) -> None:
        super().__init__(model_name, problem_bench)

    def ask(self, prompt: str, reask: bool) -> str:
        if not reask:
            prompt = self._INTRODUCTION_TO_QUESTION[self.problem_bench()] + prompt
        completion = openai.ChatCompletion.create(
            model=self.llm_id(),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content

    def _load_model(self) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
