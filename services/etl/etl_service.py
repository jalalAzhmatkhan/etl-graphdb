import os
from typing import Any, Literal

from services.etl.extractor import extractor_service
from services.etl.transformer import transformer_service

class ETLPipelineService:
    """
    ETL Pipeline Service
    """
    def create_pipeline(
        self,
        data_source_dir: str,
        input_data_type: Literal['csv', 'excel', 'pdf'] = 'pdf',
        output_data_type: Literal['markdown', 'pandas-dataframe', 'text'] = 'markdown',
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
        print(f"[ETLPipelineService] Extracting from {extracted_file_output}")
        extractor_service.extract(
            url=os.path.join(
                data_source_dir,
                source_filename
            ),
            file_type=input_data_type,
            output=extracted_file_output
        )
        print(f"[ETLPipelineService] Done extracting from {extracted_file_output}")

        # Transform the extracted data
        print("[ETLPipelineService] Transforming data")
        transformed_output = os.path.join(
            output_dir,
            f"{os.path.splitext(output_filename)[0]}_transformed.csv"
        )
        transformed_data = transformer_service.transform(
            data=extracted_file_output,
            data_type=output_data_type,
            output_filepath=transformed_output,
        )
        print(f"[ETLPipelineService] Done transforming from {extracted_file_output}")

        print(f"[ETLPipelineService] Transformed data from {extracted_file_output}: {transformed_data}")

        # Return the transformed data
        return transformed_data

etl_service = ETLPipelineService()
