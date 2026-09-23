"""
Metadata Normalization Test.
"""

from pathlib import Path

from ingestion.loader_factory import LoaderFactory
from ingestion.file_scanner import FileScanner


def main():

    print("=" * 60)
    print("METADATA NORMALIZATION TEST")
    print("=" * 60)

    # --------------------------------------------------
    # Test supported extensions
    # --------------------------------------------------

    test_files = [
        "sample.txt",
        "document.pdf",
        "image.png",
        "photo.jpg",
        "photo.jpeg",
        "roadmap.webp",
    ]

    print("\nSupported file types:")

    for file_name in test_files:

        extension = Path(file_name).suffix.lower()

        try:

            loader = LoaderFactory.get_loader(file_name)

            print(f"  {extension:6} -> " f"{loader.__class__.__name__}")

        except ValueError as exc:

            print(f"  {extension:6} -> ERROR: {exc}")

    # --------------------------------------------------
    # Scan actual knowledge base
    # --------------------------------------------------

    print("\nScanning data/raw...")

    files = FileScanner.scan("data/raw")

    for file in files:

        print(f"  {file.name:45} " f"{file.suffix.lower()}")

    print("\n" + "=" * 60)
    print("METADATA NORMALIZATION TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
