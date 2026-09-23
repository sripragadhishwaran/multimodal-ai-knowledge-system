"""
PDF Loader.

Loads PDF files using PyPDF and converts each page
into the project's standardized Document model.
"""

from pathlib import Path

from pypdf import PdfReader

from config.logging_config import logger
from models.document import Document


class PDFLoader:
    """
    Loads PDF documents page by page.
    """

    def load(self, pdf_path: str) -> list[Document]:
        """
        Load a PDF and return one Document per page.
        """

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        logger.info(f"Loading PDF: {pdf_path}")

        reader = PdfReader(pdf_path)

        documents: list[Document] = []

        total_pages = len(reader.pages)

        logger.info(f"Found {total_pages} pages.")

        for page_number, page in enumerate(reader.pages, start=1):

            try:
                text = page.extract_text()

            except Exception as e:

                logger.warning(f"Failed to extract page {page_number}: {e}")

                continue

            if not text or not text.strip():

                logger.warning(f"Skipping empty page {page_number}")

                continue

            cleaned_text = text.strip()

            section_type = self._classify_section(cleaned_text)

            document = Document(
                content=cleaned_text,
                source=str(pdf_path),
                source_type="pdf",
                metadata={
                    "file_name": pdf_path.name,
                    "page": page_number,
                    "total_pages": total_pages,
                    "section_type": section_type,
                },
            )

            documents.append(document)

            logger.debug(
                f"Page {page_number}/{total_pages} " f"classified as '{section_type}'."
            )

        logger.success(f"Successfully loaded {len(documents)} page(s).")

        return documents

    @staticmethod
    def _classify_section(text: str) -> str:
        """
        Classify the broad section type of a PDF page.

        Currently detects reference-only pages using explicit
        reference headings. Unknown pages are treated as normal
        content.
        """

        normalized_text = " ".join(text.lower().split())

        reference_markers = (
            "references:",
            "references",
            "bibliography:",
            "bibliography",
            "works cited:",
            "works cited",
        )

        for marker in reference_markers:

            if normalized_text.startswith(marker):
                return "references"

        return "content"
