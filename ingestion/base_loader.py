"""
Abstract base class for all document loaders.

Every loader (Text, PDF, Image, Web, etc.)
inherits from this class.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from config.logging_config import logger
from models.document import Document


class BaseLoader(ABC):
    """
    Base class for all loaders.
    """

    supported_extensions: set[str] = set()

    def validate_file(self, file_path: str | Path) -> Path:
        """
        Validate the input file.

        Returns
        -------
        Path
            Validated Path object.
        """

        path = Path(file_path)

        logger.info(f"Validating file: {path}")

        if not path.exists():
            logger.error(f"File not found: {path}")
            raise FileNotFoundError(path)

        if (
            self.supported_extensions
            and path.suffix.lower() not in self.supported_extensions
        ):
            logger.error(f"Unsupported extension: {path.suffix}")

            raise ValueError(
                f"Supported extensions: {self.supported_extensions}"
            )

        logger.success("Validation successful")

        return path

    @abstractmethod
    def load(self, file_path: str | Path) -> Document:
        """
        Every loader must implement this.
        """
        pass