"""
Test Web Loader.
"""

from ingestion.web_loader import WebLoader


def main() -> None:

    url = "https://example.com/"

    loader = WebLoader()

    documents = loader.load(url)

    print("=" * 60)
    print("WEB LOADER TEST")
    print("=" * 60)

    print(f"Documents loaded: {len(documents)}")

    for index, document in enumerate(
        documents,
        start=1,
    ):

        print()
        print(f"## Document #{index}")
        print()

        print("Content:")
        print(document.content[:3000])

        print()
        print("Source:")
        print(document.metadata.get("source"))

        print()
        print("Metadata:")
        print(document.metadata)


if __name__ == "__main__":
    main()
