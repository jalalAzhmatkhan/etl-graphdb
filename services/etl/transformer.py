import os
import time
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

from constants import (
    SYSTEM_PROMPT,
    TRANSFORMER_FROM_MARKDOWN_PROMPT,
    TRANSFORMER_QUERY_ACMV_PROMPT,
)
from services.llm.llm_service import LLMService
from settings import settings
from utilities import batch_dataframe, create_concatenated_string_list_vectorized

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

    def excel_data_transformer(
        self,
        df_data: pd.DataFrame,
    )->pd.DataFrame:
        """
        Transform Excel data into a DataFrame and Perform preprocessing.
        :param df_data:
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

    def query_acmv_data_dask(
        self,
        queried_data: str,
        acmv_file: str,
    )->Dict[str, Any]:
        """
        Query ACMV data from the transformed Bacnet data.
        :return:
        """
        # Placeholder for querying ACMV data
        splitted_query_data = queried_data.split("|")
        sensor_nomen_name = splitted_query_data[3]
        parsed_prompt = TRANSFORMER_QUERY_ACMV_PROMPT.replace("<nomenclature_name>", sensor_nomen_name)
        llm_client = LLMService(
            model_name="gemini-2.0-flash",
            selected_service="gemini",
        )
        attached_context = {
            "mime_type": "text/csv",
            "attachment": acmv_file
        }
        response_from_llm = llm_client.inference(
            context=attached_context,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=parsed_prompt,
            temperature=settings.LLM_TEMPERATURE,
        )
        if isinstance(response_from_llm, dict):
            response_from_llm["nomenclature_naming"] = sensor_nomen_name
            response_from_llm["equipment_location"] = splitted_query_data[1]
            response_from_llm["object_name"] = splitted_query_data[4]
            response_from_llm["read_or_write_permission"] = splitted_query_data[5]
            response_from_llm["upper_limit"] = splitted_query_data[6]
            response_from_llm["lower_limit"] = splitted_query_data[7]
            response_from_llm["object_type"] = splitted_query_data[8]
            response_from_llm["object_instance"] = splitted_query_data[10]
            response_from_llm["bacnet_ip_address"] = splitted_query_data[11]
            response_from_llm["bacnet_port"] = splitted_query_data[12]
            response_from_llm["mac_address"] = splitted_query_data[13]
            response_from_llm["object_description"] = splitted_query_data[14]
            response_from_llm["units"] = splitted_query_data[15]
            response_from_llm["cov_or_polling"] = splitted_query_data[16]
            return response_from_llm
        else:
            return {
                "status": "not_found",
                "message": "No data found for the queried nomenclature name."
            }

    def merge_data_transformer(
        self,
        data_bacnet: pd.DataFrame,
        acmv_file: str,
    )->pd.DataFrame:
        """
        Merge data from two DataFrames.
        :param data_bacnet: Load the transformed Bacnet data
        :param acmv_file: Path to the transformed ACMV data
        :return:
        """
        if not os.path.exists(acmv_file) and not os.path.isfile(acmv_file):
            raise ValueError(f"[TransformerService] File does not exist: {acmv_file}")

        batched_data = batch_dataframe(data_bacnet, 1000)

        bacnet_data_in_acmv = []

        # Process the data in batches
        for batch in batched_data:
            sensors_information = create_concatenated_string_list_vectorized(batch)
            sensor_name_bag = dbag.from_sequence(sensors_information).map(
                lambda sensor_info: self.query_acmv_data_dask(
                    sensor_info,
                    acmv_file
                )
            )
            found_query_results = [res for res in sensor_name_bag if res is not None and "status" in res and res["status"] == "found"]
            if len(found_query_results) > 0:
                bacnet_data_in_acmv.extend(found_query_results)
            time.sleep(60)  # Sleep for 60 seconds to avoid rate limiting

        # Convert the list of dictionaries to a DataFrame
        df_bacnet_data_in_acmv = pd.DataFrame(bacnet_data_in_acmv)
        return df_bacnet_data_in_acmv

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
            response = self.excel_data_transformer(pd.read_csv(data))

        if output_filepath:
            if os.path.exists(output_filepath) and os.path.isfile(output_filepath):
                os.remove(output_filepath)  # Delete existing file
            response.to_csv(output_filepath, index=False)

        return response

transformer_service = TransformerService()
