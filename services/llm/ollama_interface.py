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
        ollama_instance = ollama.Client(
            base_url=f"{protocol}{host}:{port}",
            model=model,
            temperature=temperature,
        )
        model_list_on_ollama = [ollama_mdl.model for ollama_mdl in ollama_instance.list().models]
        if model not in model_list_on_ollama:
            print(f"[OLLAMAInterface] Model '{model}' is not available on OLLAMA server.")
            print(f"[OLLAMAInterface] Downloading the model '{model}' on OLLAMA server.")
            ollama_instance.pull(model)
            print(f"[OLLAMAInterface] Model '{model}' is downloaded successfully.")

        gpu_available = 0
        if torch.cuda.is_available():
            print(f"[OLLAMAInterface] CUDA is available. Using GPU for inference.")
            gpu_available = torch.cuda.device_count()

        self.llm = ChatOllama(
            base_url=f"{protocol}{host}:{port}",
            num_gpu=gpu_available,
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
                '').strip()
            data = json.loads(inference_output)
            return data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

    def inference(
        self,
        user_prompt: str,
        files: Optional[List[str]] = None
    ) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Perform inference using the OLLAMA model.
        :param user_prompt:
        :param files:
        :return:
        """
        messages = []
        if self.system_prompt:
            messages.append(("system", self.system_prompt))

        if files:
            i = 0
            for file in files:
                try:
                    if os.path.exists(file) and os.path.isfile(file) and file.endswith('.txt'):
                        with open(file, 'r') as f:
                            file_content = f.read()
                        i += 1
                        user_prompt += f"\n\nAttachment #{i}:\n{file_content}"

                except Exception as e:
                    print(f"[OLLAMAInterface] Error reading file {file}: {e}")
                    continue

        messages.append(("user", user_prompt))
        response = self.llm.invoke(messages)
        return self.parse_inference_output(response.content)
