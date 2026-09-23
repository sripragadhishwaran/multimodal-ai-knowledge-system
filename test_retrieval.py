"""
Test the upgraded retrieval layer.
"""

from retrieval.retriever import Retriever


def main():

    retriever = Retriever()

    query = "What is LangGraph?"

    results = retriever.retrieve(
        query=query,
        top_k=3,
    )

    print("=" * 60)
    print("RETRIEVAL TEST")
    print("=" * 60)

    print(f"\nQuery: {query}")
    print(f"Results: {len(results)}")

    for index, result in enumerate(
        results,
        start=1,
    ):

        print("\n" + "-" * 60)

        print(f"Result #{index}")

        print("\nContent:")
        print(result.content)

        print("\nScore:")
        print(result.score)

        print("\nSource:")
        print(result.source)

        print("\nDocument ID:")
        print(result.document_id)

        print("\nChunk Index:")
        print(result.chunk_index)

        print("\nChunk Length:")
        print(result.chunk_length)

        print("\nMetadata:")
        print(result.metadata)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()