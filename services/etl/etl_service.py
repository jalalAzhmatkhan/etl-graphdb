import os
from typing import Any

from services.etl.extractor import extractor_service
from services.etl.transformer import transformer_service
from settings import settings

class ETLPipelineService:
    """
    ETL Pipeline Service
    """
    def create_pipeline(self)->Any:
        """
        Creates the ETL pipeline.
        :return:
        """
        # Extract data from the source
        print("[ETLPipelineService] Extracting from PDF")
        extracted_pdf_output = os.path.join(
            settings.OUTPUT_DIR,
            "bacnet_pointlist.md"
        )
        extractor_service.extract(
            url=os.path.join(
                settings.DATASOURCE_DIR,
                "BacNet_PointList_C1.pdf"
            ),
            file_type='pdf',
            output=extracted_pdf_output
        )
        print("[ETLPipelineService] Done extracting from PDF")

        # Transform the extracted data
        print("[ETLPipelineService] Transforming PDF data")
        transformed_data = transformer_service.transform(
            data=extracted_pdf_output,
            data_type='markdown'
        )
        print("[ETLPipelineService] Done transforming from PDF")

        print(f"[ETLPipelineService] Transformed data from PDF: {transformed_data}")

        # Return the transformed data
        return transformed_data

etl_service = ETLPipelineService()
