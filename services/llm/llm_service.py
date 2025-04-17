import json
from typing import Any, Dict, List, Literal, Optional, Union

from services.llm.ollama_interface import OLLAMAInterface
from services.llm.gemini_interface import gemini_client

class LLMService:
    def __init__(
        self,
        model_name: str,
        selected_service: Literal["gemini", "ollama"] = "ollama",
        service_host: Optional[str] = "localhost",
        service_port: Optional[int] = 8000,
        service_protocol: Optional[str] = "http://",  # type: ignore[assignment]
    ):
        """
        Initialize the LLMService with the selected service.
        :param selected_service:
        """
        self.llm = None
        self.selected_service = selected_service
        self.service_host = service_host
        self.service_port = service_port
        self.service_protocol = service_protocol
        self.model_name = model_name

    def ollama_inference(
        self,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.05,
        user_prompt: Optional[str] = None,
    )->Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Perform inference using the OLLAMA service provider.
        :param context:
        :param system_prompt:
        :param temperature:
        :param user_prompt:
        :return:
        """
        if not self.service_host:
            raise ValueError("Service host is not set.")
        if not self.service_port:
            raise ValueError("Service port is not set.")
        if not self.service_protocol:
            raise ValueError("Service protocol is not set.")
        if self.service_protocol not in ["http://", "https://"]:
            raise ValueError("Service protocol must be either \"http://\" or \"https://\".")

        self.llm = OLLAMAInterface(
            host=self.service_host,
            port=self.service_port,
            protocol=self.service_protocol,  # type: ignore
            system_prompt=system_prompt,
            temperature=temperature,
            model=self.model_name
        )
        return self.llm.inference(
            user_prompt,
            context
        )

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
            print(f"[LLMService] Error decoding JSON: {e}")
            print(f"[LLMService] Raw inference output: {inference_output}")
            return None

    def inference(
        self,
        context: Optional[Union[str, Dict[str, Any]]] = None,
        *,
        system_prompt: str,
        temperature: float,
        user_prompt: Optional[str] = None,
    )->Any:
        """
        Perform inference using the selected service provider.
        :return:
        """
        if self.selected_service == "ollama":
            return self.ollama_inference(
                context=context,
                system_prompt=system_prompt,
                temperature=temperature,
                user_prompt=user_prompt,
            )
        elif self.selected_service == "gemini":
            all_prompts = system_prompt + "\n" + user_prompt
            attachment_data = None
            mime_type = None
            if context and isinstance(context, dict):
                mime_type = context.get("mime_type", "text/plain")
                with open(context["attachment"], "rb") as f:
                    attachment_data = f.read()
            llm_response = gemini_client.generate_response(
                attachment=attachment_data,
                attachment_mime_type=mime_type,
                model=self.model_name,
                prompt=all_prompts
            )
            return self.parse_inference_output(llm_response)
        else:
            raise ValueError(f"Service '{self.selected_service}' is not supported yet.")
