import os
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Union,
)

import dask.bag as dbag
import pandas as pd

from constants import SYSTEM_PROMPT, TRANSFORMER_FROM_MARKDOWN_PROMPT
from services.llm.llm_service import LLMService
from settings import settings

class TransformerService:
    def dask_transformer(
        self,
        context: str,
        llm_client_interface: LLMService,
    )->Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        transformed_data = None
        try:
            transformed_data = llm_client_interface.inference(
                context=context,
                system_prompt=SYSTEM_PROMPT,
                temperature=settings.LLM_TEMPERATURE,
                user_prompt=TRANSFORMER_FROM_MARKDOWN_PROMPT
            )
        except Exception as e:
            print(f"[TransformerService] Error transforming data using Dask: {e}")
        return transformed_data

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

            contexts = []
            for row_i in range(1, len(file_contents)):
                columns = file_contents[0] if not file_contents[0].endswith("\n") else file_contents[0][:-1]
                attached_context = columns + "\n" + file_contents[row_i]
                contexts.append(attached_context)

            print(f"[TransformerService] Processing {len(contexts)} contexts in parallel...")
            context_bag = dbag.from_sequence(contexts).repartition(npartitions=5).persist()
            # Perform the transformation in parallel
            transformed_result_bag = context_bag.map(
                lambda context: self.dask_transformer(
                    context,
                    llm_client
                )
            ).compute()

            responses = [result for result in transformed_result_bag if result is not None]

        if len(responses) > 0:
            # Convert the list of dictionaries to a DataFrame
            df_response = pd.DataFrame(responses)
        return df_response

    def excel_data_filler(
        self,
        df_data: pd.DataFrame,
    )->pd.DataFrame:
        """
        Transform Excel data into a DataFrame and Perform preprocessing.
        :param df_data:
        :param zone:
        :return:
        """
        # Perform preprocessing on the DataFrame
        # Drop all rows where all columns except "Zone" are Null
        df_data = df_data.loc[df_data.drop(columns=['Zone']).notna().any(axis=1)]

        # Do forward-fill on the null values in the "Location" column
        df_data["Location"] = df_data["Location"].fillna(method="ffill")
        df_data["Location"] = df_data["Location"].str.strip()
        # Do forward-fill on the null values in the "1st Layer" column
        df_data["1st Layer"] = df_data["1st Layer"].fillna(method="ffill")
        df_data["1st Layer"] = df_data["1st Layer"].str.strip()
        # Do forward-fill on the null values in the "Serving Area" column
        df_data["Serving Area"] = df_data["Serving Area"].fillna(method="ffill")
        df_data["Serving Area"] = df_data["Serving Area"].str.strip()

        return df_data

    def transform(
        self,
        data: Optional[Any] = None,
        data_type: Literal['markdown', 'pandas-dataframe', 'text'] = 'text',
        output_filepath: Optional[str] = None
    )->pd.DataFrame:
        response = pd.DataFrame()

        if data_type == 'markdown':
            if not data:
                raise ValueError("Extracted data is not provided.")

            # Convert markdown to DataFrame
            response = self.text_transformer_from_file(data)
        elif data_type == 'pandas-dataframe':
            if not os.path.exists(data) and not os.path.isfile(data):
                raise ValueError(f"[TransformerService] File does not exist: {data}")

            # Process the Excel file
            response = self.excel_data_filler(pd.read_csv(data))

        if output_filepath:
            if os.path.exists(output_filepath) and os.path.isfile(output_filepath):
                os.remove(output_filepath)  # Delete existing file
            response.to_csv(output_filepath, index=False)

        return response

transformer_service = TransformerService()
