import os
from typing import Any, Literal, Optional, Tuple

from PyPDF2 import DocumentInformation, PdfReader, PageObject

class ExtractorService:
    def extract_pypdf_page_object(self, page: PageObject)-> Any:
        """
        Extracts text from a PyPDF2 PageObject.
        Args:
            page (PageObject): The PyPDF2 PageObject to extract text from.
        Returns:
            str: The extracted text.
        """
        # Implementation for extracting text from a page
        text = page.extract_text()
        return text

    def extract_pdf(
        self,
        url: str
    ) -> Tuple[Any, Optional[DocumentInformation]]:
        """
        Extracts data from a PDF file at the given URL.
        Args:
            url (str): The URL of the PDF file to extract data from.
        Returns:
            dict: The extracted data.
        """
        # Implementation for extracting data from PDF
        pdf_reader = PdfReader(url)
        pdf_metadata = pdf_reader.metadata

        print(f"PDF Metadata: {pdf_metadata}")  # Extract the PDF metadata
        pdf_pages = pdf_reader.pages

        # Extract text from each page using dask
        extracted_text = []
        for page in pdf_pages:
            extracted_text.append(self.extract_pypdf_page_object(page))

        return extracted_text, pdf_metadata

    def extract(
        self,
        url: str,
        file_type: Literal['pdf', 'excel'] = 'pdf',
        output: Optional[str] = None,
    ) -> Any:
        """
        Extracts data from the given URL using the specified extractor.
        Args:
            url (str): The URL to extract data from.
            file_type (Literal['pdf', 'excel']): The type of file to extract data from. Defaults to 'pdf'.
            output (Optional[str]): The path to save the extracted data. Defaults to None.
        """
        if file_type == 'pdf':
            extracted_text, pdf_metadata = self.extract_pdf(
                url
            )
            if output:
                extracted_text, pdf_metadata = self.extract_pdf(url)
                # Delete any existing markdown file
                if os.path.exists(output):
                    os.remove(output)
                with open(output, "w+", encoding="utf-8") as dumped_file:
                    for page in extracted_text:
                        dumped_file.write(page)
            return extracted_text, pdf_metadata

extractor_service = ExtractorService()
