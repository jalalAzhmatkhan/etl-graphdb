import os
from typing import Any, Literal, Optional

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
        used_input_columns: Optional[str] = None,
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
            if not used_input_columns and input_data_type == "excel":
                raise ValueError(
                    f"[ETLPipelineService] Used columns are required for Excel extraction."
                )
            extractor_service.extract(
                url=os.path.join(
                    data_source_dir,
                    source_filename
                ),
                file_type=input_data_type,
                output=extracted_file_output,
                sheet="ACMV" if input_data_type == "excel" else None,
                used_columns=used_input_columns if input_data_type == "excel" else None,
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

etl_service = ETLPipelineService()
