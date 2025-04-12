import os

from services import extractor_service

if __name__ == '__main__':
    pdf_file = os.path.join(os.getcwd(), 'datasource', "BacNet_PointList_C1.pdf")
    extracted_text, extracted_metadata = extractor_service.extract(
        pdf_file,
        file_type='pdf',
        output=os.path.join(os.getcwd(), 'outputs', "from_pdf.md")
    )
    print(f"Extracted Text: {extracted_text}")  # Print the extracted text
    print(f"Extracted Metadata: {extracted_metadata}")  # Print the extracted metadata
