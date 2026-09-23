"""
Test Image RAG.

Verifies that OCR-extracted image knowledge
can be retrieved and used by the RAG pipeline.
"""

from services.rag_service import RAGService


def main() -> None:

    print("=" * 60)
    print("IMAGE RAG TEST")
    print("=" * 60)

    rag = RAGService(top_k=3)

    question = "What topics are included in the " "Generative AI roadmap?"

    print()
    print(f"Question: {question}")
    print()

    answer = rag.ask(question)

    print("Answer:")
    print(answer)

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
