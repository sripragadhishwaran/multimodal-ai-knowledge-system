"""
Test Image Loader.

Verifies that ImageLoader can:
1. Load an image
2. Extract text using OCR
3. Return standardized Document objects
"""

from ingestion.image_loader import ImageLoader


def main() -> None:

    image_path = "data/raw/images/" "Generative-AI-Roadmap-1024x576.webp"

    loader = ImageLoader()

    documents = loader.load(image_path)

    print("=" * 60)

    print(f"Documents loaded: {len(documents)}")

    if not documents:
        print("No documents were loaded.")
        return

    for index, document in enumerate(documents, start=1):

        print()
        print(f"Document #{index}")
        print("-" * 60)

        print("Content:")
        print(document.content)

        print()
        print("Source:")
        print(document.source)

        print()
        print("Source Type:")
        print(document.source_type)

        print()
        print("Metadata:")
        print(document.metadata)

        print()
        print("Document ID:")
        print(document.id)

    print("=" * 60)


if __name__ == "__main__":
    main()
