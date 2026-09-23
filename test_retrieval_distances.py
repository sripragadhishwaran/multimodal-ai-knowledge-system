"""
Temporary Retrieval Distance Calibration.

Purpose:
Inspect raw ChromaDB distance distributions without
changing Retriever thresholds or production code.
"""

from vectorstore.index_manager import IndexManager

QUERIES = [
    "What is Artificial Intelligence?",
    "What is Machine Learning?",
    "What is Deep Learning?",
    "How is Artificial Intelligence used in healthcare and education?",
    "What are the concerns about Artificial Intelligence?",
]


def inspect_query(manager: IndexManager, query: str, top_k: int = 15):

    print()
    print("=" * 90)
    print(f"QUERY: {query}")
    print("=" * 90)

    results = manager.search(
        query=query,
        top_k=top_k,
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        print("NO RESULTS")
        return

    print(f"RAW CANDIDATES: {len(documents)}")
    print()

    for index, (document, distance, metadata) in enumerate(
        zip(documents, distances, metadatas),
        start=1,
    ):

        print(f"#{index}")
        print(f"Distance     : {distance:.4f}")
        print(f"Content Type : {metadata.get('content_type', 'unknown')}")
        print(f"Source       : {metadata.get('source', 'unknown')}")
        print(f"File Name    : {metadata.get('file_name', 'unknown')}")

        if metadata.get("page") is not None:
            print(f"Page         : {metadata.get('page')}")

        print("Preview      : " + document[:180].replace("\n", " "))

        print()


def main():

    print()
    print("#" * 90)
    print("RAW RETRIEVAL DISTANCE CALIBRATION")
    print("#" * 90)

    manager = IndexManager()

    for query in QUERIES:
        inspect_query(manager, query)


if __name__ == "__main__":
    main()
