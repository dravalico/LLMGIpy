from typing import Any
from llmpony.llm.models.AbstractLanguageModel import AbstractLanguageModel
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, AutoConfig



class HuggingFaceLLM(AbstractLanguageModel):
    def __init__(self, model_name: str, problem_bench: str, prompt_type: str, load_model: bool = True) -> None:
        super().__init__(model_name=model_name, problem_bench=problem_bench, prompt_type=prompt_type, load_model=load_model)

    def ask(self, prompts: list[str]) -> str:
        torch.cuda.empty_cache()
        messages = self.build_chat_from_prompts(prompts)

        input_ids = self.__tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.__model.device)

        if self.__tokenizer.convert_tokens_to_ids("<|eot_id|>") is None:
            self.__tokenizer.add_special_tokens({"additional_special_tokens": ["<|eot_id|>"]})
            self.__model.resize_token_embeddings(len(self.__tokenizer))


        terminators = [
            self.__tokenizer.eos_token_id,
            self.__tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]


        outputs = self.__model.generate(
            input_ids,
            max_new_tokens=600,
            eos_token_id=terminators
        )

        response = outputs[0][input_ids.shape[-1]:]
        return self.__tokenizer.decode(response, skip_special_tokens=True)

    def _load_model(self) -> Any:
        super()._load_model()
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)

        model_id = self.llm_id()

        self.__tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True,
            token=os.getenv('HF_TOKEN')
        )
        #self.__tokenizer.pad_token_id = self.__tokenizer.eos_token_id
        self.__model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto",
            token=os.getenv('HF_TOKEN'),
            quantization_config=quantization_config,
        )
        #self.__config.pad_token_id = self.__tokenizer.pad_token_id
        #self.__config.sliding_window = None
        #self.__model = AutoModelForCausalLM.from_config(self.__config)
