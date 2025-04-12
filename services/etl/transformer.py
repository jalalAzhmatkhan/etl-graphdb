import os
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
        df_response = pd.DataFrame()
        if not os.path.exists(file) and not os.path.isfile(file):
            raise ValueError(f"[TransformerService] File does not exist: {file}")

        file_contents = []
        with open(file, "r", encoding="utf-8") as f:
            file_contents = f.readlines()

        responses = []
        if len(file_contents) > 0:
            llm_client = LLMService(
                model_name=settings.LLM_MODEL,
                selected_service=settings.LLM_SERVICE,
                service_host=settings.LLM_HOST,
                service_port=settings.LLM_PORT,
                service_protocol=settings.LLM_CONNECT_PROTOCOL
            )
            print(f"[TransformerService] LLM client initialized with model: {settings.LLM_MODEL}")

            for row_i in range(1, len(file_contents)):
                columns = file_contents[0] if not file_contents[0].endswith("\n") else file_contents[0][:-1]
                attached_context = columns + "\n" + file_contents[row_i]
                transformed_data = llm_client.inference(
                    context=attached_context,
                    system_prompt=SYSTEM_PROMPT,
                    temperature=settings.LLM_TEMPERATURE,
                    user_prompt=TRANSFORMER_FROM_MARKDOWN_PROMPT
                )
                print(f"[TransformerService] Transforming file: {file} SUCCESS")
                responses.append(transformed_data)

        if len(responses) > 0:
            # Convert the list of dictionaries to a DataFrame
            df_response = pd.DataFrame(responses)
        return df_response

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
