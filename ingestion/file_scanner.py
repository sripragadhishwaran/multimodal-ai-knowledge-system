"""
File Scanner.

Scans a directory recursively and returns
all supported document files.
"""

from pathlib import Path


class FileScanner:
    """
    Finds supported files for ingestion.
    """

    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }

    @classmethod
    def scan(cls, directory: str) -> list[Path]:
        """
        Scan a directory recursively.
        """

        directory = Path(directory)

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        files = []

        for file in directory.rglob("*"):

            if file.is_file() and file.suffix.lower() in cls.SUPPORTED_EXTENSIONS:
                files.append(file)

        return sorted(files)
