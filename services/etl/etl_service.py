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

        # Transform the extracted data
        transformed_data = transformer_service.transform(
            data=extracted_pdf_output,
            data_type='markdown'
        )

        # Return the transformed data
        return transformed_data

etl_service = ETLPipelineService()
