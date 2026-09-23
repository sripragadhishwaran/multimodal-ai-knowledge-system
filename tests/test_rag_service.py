"""
RAG Service Test.

Tests the complete application-level RAG pipeline.
"""

from services.rag_service import RAGService


def main():

    service = RAGService(top_k=3)

    questions = [
        "What is LangGraph?",
        "What topics are included in the Generative AI roadmap?",
        "What does this PDF explain?",
        "Show me the diagram about AI.",
        "Compare the information in the PDF with the Generative AI roadmap image.",
    ]

    for question in questions:

        print()
        print("=" * 70)
        print(f"QUESTION: {question}")
        print("=" * 70)

        try:

            response = service.ask(question)

            # ==================================================
            # ANSWER
            # ==================================================

            print()
            print("ANSWER:")
            print(response.answer)

            # ==================================================
            # CONTENT TYPES
            # ==================================================

            print()
            print("CONTENT TYPES:")
            print(response.content_types)

            # ==================================================
            # IMAGE SOURCES
            # ==================================================

            print()
            print("IMAGE SOURCES:")

            if response.image_sources:

                for source in response.image_sources:
                    print(f"  - {source}")

            else:

                print("  None")

            # ==================================================
            # DOCUMENT SOURCES
            # ==================================================

            print()
            print("DOCUMENT SOURCES:")

            if response.document_sources:

                for source in response.document_sources:
                    print(f"  - {source}")

            else:

                print("  None")

            # ==================================================
            # WEB SOURCES
            # ==================================================

            print()
            print("WEB SOURCES:")

            if response.web_sources:

                for source in response.web_sources:
                    print(f"  - {source}")

            else:

                print("  None")

            # ==================================================
            # RETRIEVAL INFORMATION
            # ==================================================

            print()
            print("SOURCE COUNT:")
            print(response.source_count)

            print()
            print("MULTIMODAL:")
            print(response.multimodal)

            print()
            print("CONTEXT RELEVANT:")
            print(response.context_relevant)

            print()
            print("RECOVERY ATTEMPTED:")
            print(response.recovery_attempted)

            print()
            print("RETRIEVAL ATTEMPTS:")
            print(response.retrieval_attempts)

            print()
            print("BEST SCORE:")
            print(response.best_score)

            # ==================================================
            # METADATA
            # ==================================================

            print()
            print("METADATA:")
            print(response.metadata)

            # ==================================================
            # SUCCESS
            # ==================================================

            print()
            print("TEST STATUS: SUCCESS")

        except Exception as exc:

            print()
            print("TEST STATUS: FAILED")
            print(type(exc).__name__, exc)

        print()
        print("=" * 70)


if __name__ == "__main__":
    main()
