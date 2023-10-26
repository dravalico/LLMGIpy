import os
import openai
from models.AbstractLanguageModel import AbstractLanguageModel


class GPT4(AbstractLanguageModel):
    def __init__(self) -> None:
        super().__init__("GPT4")

    def ask(self, question: str, reask: bool) -> str:
        if not reask:
            question = self._INTRODUCTION_TO_QUESTION + question
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": question}
            ]
        )
        return completion.choices[0].message.content

    def _load_model(self) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
