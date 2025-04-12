from typing import Any, Optional, Literal

import pandas as pd

from constants import SYSTEM_PROMPT, TRANSFORMER_FROM_MARKDOWN_PROMPT
from services.llm.llm_service import LLMService
from settings import settings

class TransformerService:
    def text_transformer_from_file(
        self,
        file: str
    )->pd.DataFrame:
        """
        Transform text into a DataFrame.
        :param file:
        :return:
        """
        llm_client = LLMService(
            model_name=settings.LLM_MODEL,
            selected_service=settings.LLM_SERVICE,
            service_host=settings.LLM_HOST,
            service_port=settings.LLM_PORT,
            service_protocol=settings.LLM_CONNECT_PROTOCOL
        )
        transformed_data = llm_client.inference(
            attached_files=[file],
            system_prompt=SYSTEM_PROMPT,
            temperature=settings.LLM_TEMPERATURE,
            user_prompt=TRANSFORMER_FROM_MARKDOWN_PROMPT
        )

        return pd.DataFrame(transformed_data)

    def transform(
        self,
        data: Optional[Any] = None,
        data_type: Literal['markdown', 'text'] = 'text',
    )->pd.DataFrame:
        response = pd.DataFrame()

        if data_type == 'markdown':
            if not data:
                raise ValueError("Extracted data is not provided.")

            # Convert markdown to DataFrame
            response = self.text_transformer_from_file(data)

        return response

transformer_service = TransformerService()
