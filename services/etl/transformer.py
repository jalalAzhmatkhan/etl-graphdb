import os
import re
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
)
from services.llm.llm_service import LLMService
from settings import settings
from utilities import (
    batch_dataframe,
    create_concatenated_string_list_vectorized,
    uniforms_nomenclature_naming,
)

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
        df_data = df_data.copy()
        # Drop all rows where all columns except "Zone" are Null
        df_data = df_data.loc[df_data.drop(columns=['Zone']).notna().any(axis=1)]

        # Do forward-fill on the null values in the "Location" column
        df_data.loc[:, "Location"] = df_data["Location"].ffill()
        df_data.loc[:, "Location"] = df_data["Location"].str.strip()
        # Do forward-fill on the null values in the "1st Layer" column
        df_data.loc[:, "1st Layer"] = df_data["1st Layer"].ffill()
        df_data.loc[:, "1st Layer"] = df_data["1st Layer"].str.strip()
        # Do forward-fill on the null values in the "Serving Area" column
        df_data.loc[:, "Serving Area"] = df_data["Serving Area"].ffill()
        df_data.loc[:, "Serving Area"] = df_data["Serving Area"].str.strip()

        df_data["1st Layer"] = df_data["1st Layer"].astype(str)
        df_data["2nd Layer"] = df_data["2nd Layer"].astype(str)
        df_data["3rd Layer"] = df_data["3rd Layer"].astype(str)
        df_data["Serving Area"] = df_data["Serving Area"].astype(str)

        # Check the value in each rows
        new_rows = []
        index_to_drop = []

        for index, row in df_data.iterrows():
            location = row['Location']
            first_layer = str(row['1st Layer'])
            second_layer = str(row['2nd Layer'])
            third_layer = row['3rd Layer']
            serving_area = row['Serving Area']
            zone = row['Zone']

            first_layer_split = [fl.strip() for fl in first_layer.split(" & ")]
            second_layer_parts = second_layer.split(" & ")
            third_layer_parts = third_layer.split(" & ")
            serving_area_parts = serving_area.split(" & ")

            serving_area_values = []
            for part in serving_area_parts:
                if " to " in part:
                    match = re.match(r"(.+)-(\d+) to (\d+)", part)
                    if match:
                        prefix = match.group(1) + "-"
                        start = int(match.group(2))
                        end = int(match.group(3))
                        for i in range(start, end + 1):
                            if i > 9:
                                serving_area_values.extend([f"{prefix}{i}"])
                            else:
                                serving_area_values.extend([f"{prefix}0{i}"])
                    else:
                        serving_area_values.append(part.strip())
                else:
                    serving_area_values.append(part)

            final_third_layers = []
            for part in third_layer_parts:
                if " to " in part:
                    match = re.match(r"(.+)-(\d+) to (\d+)", part)
                    if match:
                        prefix = match.group(1) + "-"
                        start = int(match.group(2))
                        end = int(match.group(3))
                        for i in range(start, end + 1):
                            if i > 9:
                                final_third_layers.extend([f"{prefix}{i}"])
                            else:
                                final_third_layers.extend([f"{prefix}0{i}"])
                    else:
                        final_third_layers.append(part.strip())
                else:
                    final_third_layers.append(part.strip())

            final_second_layers = []
            for part in second_layer_parts:
                if " to " in part:
                    match = re.match(r"(.+)-(\d+) to (\d+)", part)
                    if match:
                        prefix = match.group(1) + "-"
                        start = int(match.group(2))
                        end = int(match.group(3))
                        for i in range(start, end + 1):
                            if i > 9:
                                final_third_layers.extend([f"{prefix}{i}"])
                            else:
                                final_third_layers.extend([f"{prefix}0{i}"])
                    else:
                        final_second_layers.append(part.strip())
                else:
                    final_second_layers.append(part.strip())

            # Create new rows based on combinations of 1st and 2nd layers
            for fl in first_layer_split:
                for sl in final_second_layers:
                    for tl in final_third_layers:
                        for sa in serving_area_values:
                            new_rows.append({
                                'Location': location,
                                '1st Layer': fl,
                                '2nd Layer': sl,
                                '3rd Layer': tl,
                                'Serving Area': sa,
                                'Zone': zone
                            })

            index_to_drop.append(index)

        # Remove the original rows that were processed
        df_data = df_data.drop(index_to_drop)

        # Append the new rows
        df_data = pd.concat([df_data, pd.DataFrame(new_rows)], ignore_index=True)

        return df_data

    def query_acmv_data_dask(
        self,
        queried_data: str,
        acmv_file: str,
    )->Optional[pd.DataFrame]:
        """
        Query ACMV data from the transformed Bacnet data.
        :return:
        """
        # Placeholder for querying ACMV data
        splitted_query_data = queried_data.split("|")
        if splitted_query_data[3][:2].lower() == "ts":
            # Do not process sensor with prefix TS-*
            # bcs no data found on the ACMV relation
            return None

        try:
            # Parse the nomenclature name into a standardized format
            sensor_nomen_name = uniforms_nomenclature_naming(splitted_query_data[3])

            df_acmv = pd.read_csv(acmv_file)
            # Define the columns to search in
            search_columns = ["1st Layer", "2nd Layer", "3rd Layer"]

            # Create a boolean mask by checking if the query string is contained in each of the specified columns
            mask = False
            splitted_query = sensor_nomen_name.split("-")
            recreated_query = splitted_query[1] + "-" + splitted_query[2] + "-" + splitted_query[3] + "-" + splitted_query[
                4]
            found_in_col = ""
            for col in search_columns:
                mask = mask | df_acmv[col].str.contains(recreated_query, na=False)
                if True in df_acmv[col].str.contains(recreated_query, na=False).tolist():
                    found_in_col = col
                    print(f"[TransformerService] Query {recreated_query} found in: {found_in_col}")

            # Filter the DataFrame using the mask
            result_df = df_acmv[mask].copy()
            if found_in_col != "":
                print("[TransformerService] Try to add Additional BACnet data...")
                result_df["nomenclature_naming"] = sensor_nomen_name
                result_df["found_in_col"] = found_in_col
                result_df["equipment_location"] = splitted_query_data[1] if splitted_query_data[1] != "nan" else None
                result_df["object_name"] = splitted_query_data[4] if splitted_query_data[4] != "nan" else None
                result_df["read_or_write_permission"] = splitted_query_data[5] if splitted_query_data[5] != "nan" else None
                result_df["upper_limit"] = splitted_query_data[6] if splitted_query_data[6] != "nan" else None
                result_df["lower_limit"] = splitted_query_data[7] if splitted_query_data[7] != "nan" else None
                result_df["object_type"] = splitted_query_data[8] if splitted_query_data[8] != "nan" else None
                result_df["object_instance"] = splitted_query_data[10] if splitted_query_data[10] != "nan" else None
                result_df["bacnet_ip_address"] = splitted_query_data[11] if splitted_query_data[11] != "nan" else None
                result_df["bacnet_port"] = splitted_query_data[12] if splitted_query_data[12] != "nan" else None
                result_df["mac_address"] = splitted_query_data[13] if splitted_query_data[13] != "nan" else None
                result_df["object_description"] = splitted_query_data[14] if splitted_query_data[14] != "nan" else None
                result_df["units"] = splitted_query_data[15] if splitted_query_data[15] != "nan" else None
                result_df["cov_or_polling"] = splitted_query_data[16] if splitted_query_data[16] != "nan" else None
                print("[TransformerService] Done adding Additional BACnet data...")

            return result_df if len(result_df) > 0 else None
        except Exception as e:
            print(f"[TransformerService] Error querying ACMV data using Dask for data {splitted_query_data[3]}: {e}")

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

        sensors_information = create_concatenated_string_list_vectorized(data_bacnet)
        all_found_bacnet_data = pd.DataFrame()
        for s_info in sensors_information:
            df_found = self.query_acmv_data_dask(s_info, acmv_file)
            if df_found is not None:
                all_found_bacnet_data = pd.concat([all_found_bacnet_data, df_found], ignore_index=True)

        # Convert the list of dictionaries to a DataFrame
        print("[TransformerService] Done Merging data from Bacnet and ACMV...")
        print(f"[TransformerService] Data merged: {len(all_found_bacnet_data)}...")
        return all_found_bacnet_data

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
