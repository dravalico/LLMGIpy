import os
import openai
from models.AbstractLanguageModel import AbstractLanguageModel


class ChatGPT(AbstractLanguageModel):
    def __init__(self) -> None:
        super().__init__("ChatGPT")

    def ask(self, question: str, reask: bool) -> str:
        if not reask:
            question = self._INTRODUCTION_TO_QUESTION + question
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": self._INTRODUCTION_TO_QUESTION + question}
            ]
        )
        res = completion.choices[0].message.content
        return res

    def _load_model(self) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
