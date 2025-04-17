import os
from typing import Any, Literal, Optional

import pandas as pd

from services.etl.extractor import extractor_service
from services.etl.transformer import transformer_service

class ETLPipelineService:
    """
    ETL Pipeline Service
    """
    def create_pipeline(
        self,
        data_source_dir: str,
        cached_extraction: bool = False,
        input_data_type: Literal['csv', 'excel', 'pdf'] = 'pdf',
        output_data_type: Literal['markdown', 'pandas-dataframe', 'text'] = 'markdown',
        cached_transformation: bool = False,
        extend_existing_output_file: Optional[bool] = False,
        *,
        source_filename: str,
        output_dir: str,
        output_filename: str
    )->Any:
        """
        Creates the ETL pipeline.
        :return:
        """
        # Extract data from the source
        extracted_file_output = os.path.join(
            output_dir,
            output_filename
        )
        if not cached_extraction or not os.path.exists(extracted_file_output):
            print(f"[ETLPipelineService] Extracting from {extracted_file_output}")
            extractor_service.extract(
                url=os.path.join(
                    data_source_dir,
                    source_filename
                ),
                file_type=input_data_type,
                output=extracted_file_output,
                sheet="ACMV" if input_data_type == "excel" else None,
                extend_existing_output_file=extend_existing_output_file,
            )
            print(f"[ETLPipelineService] Done extracting from {extracted_file_output}")

        # Transform the extracted data
        transformed_output = os.path.join(
            output_dir,
            f"{os.path.splitext(output_filename)[0]}_transformed.csv"
        )

        if not cached_transformation or not os.path.exists(transformed_output):
            print("[ETLPipelineService] Transforming data")
            transformed_data = transformer_service.transform(
                data=extracted_file_output,
                data_type=output_data_type,
                output_filepath=transformed_output,
            )
            print(f"[ETLPipelineService] Done transforming from {extracted_file_output}")
            print(f"[ETLPipelineService] Transformed data from {extracted_file_output}: {transformed_data}")

    def merge_data(
        self,
        transformed_data_bacnet: str,
        transformed_data_acmv: str,
        output_filepath: Optional[str] = None
    )->pd.DataFrame:
        """
        Merges data from two DataFrames.
        :param transformed_data_bacnet: Path to the transformed Bacnet data
        :param transformed_data_acmv: Path to the transformed ACMV data
        :param output_filepath: Path to the output file. If not provided, the merged data is returned as a DataFrame.
        :return:
        """
        if not os.path.exists(transformed_data_bacnet) or not os.path.isfile(transformed_data_bacnet):
            raise ValueError(f"[ETLPipelineService] File does not exist or invalid file: {output_filepath}")

        df_bacnet = pd.read_csv(transformed_data_bacnet)

        df_merged_data = transformer_service.merge_data_transformer(
            data_bacnet=df_bacnet,
            acmv_file=transformed_data_acmv
        )

        if output_filepath:
            if os.path.exists(output_filepath) and os.path.isfile(output_filepath):
                os.remove(output_filepath)
            df_merged_data.to_csv(output_filepath, index=False)

        df_merged_data = df_merged_data[df_merged_data["found_in_col"].notnull() & (df_merged_data["found_in_col"].str.strip() != "")]
        return df_merged_data

etl_service = ETLPipelineService()
