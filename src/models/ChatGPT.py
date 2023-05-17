import os
import openai
from models.AbstractLanguageModel import AbstractLanguageModel


class ChatGPTModel(AbstractLanguageModel):
    def __init__(self) -> None:
        super().__init__("ChatGPT")

    def ask(self, question: str) -> str:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": self._INTRODUCTION_TO_QUESTION + question}
            ]
        )
        res = completion.choices[0].message.content
        print(res)
        return res

    def _load_model(self) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
