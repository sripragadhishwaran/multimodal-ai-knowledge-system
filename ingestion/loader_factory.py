"""
Loader Factory.

Returns the appropriate loader based on the file extension.
"""

from pathlib import Path

from ingestion.pdf_loader import PDFLoader
from ingestion.text_loader import TextLoader
from ingestion.image_loader import ImageLoader


class LoaderFactory:
    """
    Factory for selecting the correct document loader.
    """

    _LOADERS = {
        ".txt": TextLoader,
        ".pdf": PDFLoader,
        ".png": ImageLoader,
        ".jpg": ImageLoader,
        ".jpeg": ImageLoader,
        ".webp": ImageLoader,
    }

    @classmethod
    def get_loader(cls, file_path: str):
        """
        Return the appropriate loader for the file.
        """

        extension = Path(file_path).suffix.lower()

        loader_class = cls._LOADERS.get(extension)

        if loader_class is None:
            raise ValueError(f"Unsupported file type: {extension}")

        return loader_class()
