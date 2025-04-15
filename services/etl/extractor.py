import os
from typing import Any, Literal, Optional, Tuple, Union

import pandas as pd
from PyPDF2 import DocumentInformation, PdfReader, PageObject

class ExtractorService:
    def extract_excel(
        self,
        url: str,
        header: Optional[int] = None,
        sheet: Optional[Union[str, int]] = None,
        used_columns: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Extracts data from an Excel file at the given URL.
        Args:
            url (str): The URL of the Excel file to extract data from.
            header (Optional[int]): The row number to use as the column names.
            sheet (Optional[Union[str, int]]): The name or index of the sheet to extract data from.
            used_columns (Optional[str]): A comma-separated list of column names to use.
        Returns:
            dict: The extracted data.
        """
        if not os.path.exists(url) and os.path.isfile(url):
            raise ValueError(f"[ExtractorService] File does not exist: {url}")
        if not url.endswith('.xlsx') and not url.endswith('.xls'):
            raise ValueError(f"[ExtractorService] Invalid file type: {url}")

        # Implementation for extracting data from Excel
        df_data = pd.read_excel(   # type: ignore
            url,
            header=header,
            index_col=None,
            sheet_name=sheet,
            usecols=used_columns,
        )

        print(f"Extracted data from Excel: {df_data}")

        return df_data

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
        file_type: Literal['csv', 'excel', 'pdf'] = 'pdf',
        output: Optional[str] = None,
        sheet: Optional[Union[str, int]] = None,
        used_columns: Optional[str] = None,
        extend_existing_output_file: bool = False,
    ) -> Any:
        """
        Extracts data from the given URL using the specified extractor.
        Args:
            url (str): The URL to extract data from.
            file_type (Literal['pdf', 'excel']): The type of file to extract data from. Defaults to 'pdf'.
            output (Optional[str]): The path to save the extracted data. Defaults to None.
            sheet (Optional[Union[str, int]]): The name or index of the sheet to extract data from.
            used_columns (Optional[str]): A colon-separated list of column names to use. e.g. 'A:E'.
            extend_existing_output_file (bool): Whether to extend the existing output file data. Defaults to False.
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
        elif file_type == 'excel':
            if not sheet:
                raise ValueError(f"[ExtractorService] Sheet name or index is required for Excel extraction.")
            if not used_columns:
                raise ValueError(f"[ExtractorService] Used columns is required for Excel extraction.")

            extracted_data = self.extract_excel(
                url=url,
                header=2,
                sheet=sheet,
                used_columns=used_columns,
            )

            if output:
                # Delete any existing CSV file
                if os.path.exists(output):
                    os.remove(output)
                if not extend_existing_output_file:
                    extracted_data.to_csv(output, index=False)
                else:
                    extracted_data.to_csv(output, mode='a', header=False, index=False)

            return extracted_data

extractor_service = ExtractorService()
