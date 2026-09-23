from services.rag_service import RAGService


def main():

    rag = RAGService(top_k=3)

    question = "What is LangGraph?"

    response = rag.ask(question)

    print("\n" + "=" * 60)
    print("RAG RESPONSE")
    print("=" * 60)

    print(f"\nQuestion:")
    print(response.question)

    print(f"\nAnswer:")
    print(response.answer)

    print(f"\nRetrieved Chunks: " f"{response.retrieved_chunks}")

    print("\nSources:")

    for source in response.sources:

        print(f"\n[Source {source.source_number}]")

        print(f"File       : " f"{source.file_name}")

        print(f"Source     : " f"{source.source}")

        print(f"Document ID: " f"{source.document_id}")

        print(f"Chunk      : " f"{source.chunk_index}")

        print(f"Length     : " f"{source.chunk_length}")

        print(f"Page       : " f"{source.page if source.page is not None else 'N/A'}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
