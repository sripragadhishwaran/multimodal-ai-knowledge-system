"""
Main Application.

Command-line interface for the
Multimodal AI Knowledge System.
"""

from services.rag_service import RAGService


def main():

    print("=" * 70)
    print("Multimodal AI Knowledge System")
    print("=" * 70)

    print("\nInitializing RAG system...")

    service = RAGService(top_k=3)

    print("\nRAG system ready.")

    while True:

        try:

            question = input("\nAsk a question (type 'exit' to quit): ").strip()

        except (KeyboardInterrupt, EOFError):

            print("\n\nGoodbye!")

            break

        # ==================================================
        # EXIT
        # ==================================================

        if question.lower() in ["exit", "quit"]:

            print("\nGoodbye!")

            break

        # ==================================================
        # EMPTY QUESTION
        # ==================================================

        if not question:

            print("\nPlease enter a question.")

            continue

        # ==================================================
        # PROCESS QUESTION
        # ==================================================

        try:

            response = service.ask(question)

            # ==================================================
            # ANSWER
            # ==================================================

            print("\n" + "=" * 70)
            print("AI ANSWER")
            print("=" * 70)

            print(response.answer)

            # ==================================================
            # CONTENT TYPES
            # ==================================================

            print("\n" + "=" * 70)
            print("CONTENT TYPES")
            print("=" * 70)

            if response.content_types:

                for content_type in response.content_types:

                    print(f"  - {content_type}")

            else:

                print("  None")

            # ==================================================
            # IMAGE SOURCES
            # ==================================================

            print("\n" + "=" * 70)
            print("IMAGE SOURCES")
            print("=" * 70)

            if response.image_sources:

                for source in response.image_sources:

                    print(f"  - {source}")

            else:

                print("  None")

            # ==================================================
            # DOCUMENT SOURCES
            # ==================================================

            print("\n" + "=" * 70)
            print("DOCUMENT SOURCES")
            print("=" * 70)

            if response.document_sources:

                for source in response.document_sources:

                    print(f"  - {source}")

            else:

                print("  None")

            # ==================================================
            # WEB SOURCES
            # ==================================================

            print("\n" + "=" * 70)
            print("WEB SOURCES")
            print("=" * 70)

            if response.web_sources:

                for source in response.web_sources:

                    print(f"  - {source}")

            else:

                print("  None")

            # ==================================================
            # RETRIEVAL INFORMATION
            # ==================================================

            print("\n" + "=" * 70)
            print("RETRIEVAL INFORMATION")
            print("=" * 70)

            print(f"Source Count       : {response.source_count}")

            print(f"Multimodal         : {response.multimodal}")

            print(f"Context Relevant   : {response.context_relevant}")

            print(f"Recovery Attempted : {response.recovery_attempted}")

            print(f"Retrieval Attempts : {response.retrieval_attempts}")

            print(f"Best Score         : {response.best_score:.4f}")

            # ==================================================
            # METADATA
            # ==================================================

            print("\n" + "=" * 70)
            print("METADATA")
            print("=" * 70)

            print(response.metadata)

            # ==================================================
            # STATUS
            # ==================================================

            print("\n" + "=" * 70)
            print("STATUS: SUCCESS")
            print("=" * 70)

        except Exception as exc:

            print("\n" + "=" * 70)
            print("ERROR")
            print("=" * 70)

            print(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":

    main()
