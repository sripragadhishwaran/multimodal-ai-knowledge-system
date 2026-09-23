"""
Web Indexing Test.
"""

from services.indexing_service import IndexingService


def main():

    print("=" * 60)
    print("WEB INDEXING TEST")
    print("=" * 60)

    url = "https://www.python.org/"

    service = IndexingService()

    print("\nStarting URL indexing...\n")

    service.index_url(url)

    print("\n" + "=" * 60)
    print("WEB INDEXING TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
