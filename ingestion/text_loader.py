"""
Loads plain text documents.
"""

from pathlib import Path

from config.logging_config import logger
from ingestion.base_loader import BaseLoader
from models.document import Document


class TextLoader(BaseLoader):

    supported_extensions = {
        ".txt",
        ".md",
    }

    def load(self, file_path: str | Path) -> list[Document]:

        path = self.validate_file(file_path)

        logger.info(f"Reading {path.name}")

        content = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        logger.success(
            f"Loaded {len(content)} characters."
        )

        document = Document(
            content=content,
            source=str(path),
            source_type="text",
            metadata={
                "file_name": path.name,
            },
        )

        return [document]