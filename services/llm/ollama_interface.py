import json
import os
from typing import Any, Dict, List, Literal, Optional, Union

from langchain_ollama.chat_models import ChatOllama
import ollama
import torch

class OLLAMAInterface:
    def __init__(
        self,
        host: str ='localhost',
        port: int =8000,
        protocol: Literal["http://", "https://"] = "http://",
        model: str = 'default',
        system_prompt: Optional[str] = None,
        temperature: float = 0.05,
    ):
        """
        Initialize the OLLAMAInterface with the given parameters.
        :param host:
        :param port:
        :param model:
        :param system_prompt:
        """
        base_url_ollama = f"{protocol}{host}:{port}"
        ollama_instance = ollama.Client(
            host=base_url_ollama,
        )
        model_list_on_ollama = [ollama_mdl.model for ollama_mdl in ollama_instance.list().models]
        if model not in model_list_on_ollama:
            print(f"[OLLAMAInterface] Model '{model}' is not available on OLLAMA server.")
            print(f"[OLLAMAInterface] Downloading the model '{model}' on OLLAMA server.")
            ollama_instance.pull(model)
            print(f"[OLLAMAInterface] Model '{model}' is downloaded successfully.")

        if not torch.cuda.is_available():
            print(f"[OLLAMAInterface] CUDA is NOT available. Using CPU for inference.")

        self.llm = ChatOllama(
            base_url=f"{protocol}{host}:{port}",
            num_predict=-1,  # -1 means no limit on the generation
            model=model,
            temperature=temperature
        )
        self.system_prompt = system_prompt

    def parse_inference_output(
        self,
        inference_output: str
    )->Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Parse the inference output from the OLLAMA model to JSON.
        :param inference_output:
        :return:
        """
        try:
            inference_output = inference_output.replace(
                '```python', ''
            ).replace(
                '```', ''
            ).replace(
                '```json',
                ''
            ).replace(
                '```JSON',
                ''
            ).strip()
            data = json.loads(inference_output)
            return data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw inference output: {inference_output}")
            return None

    def inference(
        self,
        user_prompt: str,
        context: Optional[str] = None,
    ) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Perform inference using the OLLAMA model.
        :param user_prompt:
        :param context:
        :return:
        """
        messages = []
        if self.system_prompt:
            messages.append(("system", self.system_prompt))

        if context:
            user_prompt += context if user_prompt.endswith("\n") else f"\n{context}"

        messages.append(("user", user_prompt))
        response = self.llm.invoke(messages)
        return self.parse_inference_output(response.content)
