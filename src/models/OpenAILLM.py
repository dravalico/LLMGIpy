import os
import openai
from models.AbstractLanguageModel import AbstractLanguageModel


class OpenAILLM(AbstractLanguageModel):
    def __init__(self, model_name: str, problem_bench: str, prompt_type: str, load_model: bool = True) -> None:
        super().__init__(model_name=model_name, problem_bench=problem_bench, prompt_type=prompt_type, load_model=load_model)

    def ask(self, prompts: list[str]) -> str:
        messages = self.build_chat_from_prompts(prompts)
        completion = openai.ChatCompletion.create(
            model=self.llm_id(),
            messages=messages
        )
        return completion.choices[0].message.content

    def _load_model(self) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
