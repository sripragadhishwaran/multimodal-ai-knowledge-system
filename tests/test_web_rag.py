from services.indexing_service import IndexingService
from services.rag_service import RAGService


def main():

    print()
    print("=" * 60)
    print("WEB RAG TEST")
    print("=" * 60)

    url = "https://www.python.org/"
    question = "What is Python?"

    # --------------------------------------------------
    # 1. Index web page
    # --------------------------------------------------

    print()
    print("[1] Indexing web page...")
    print(f"URL: {url}")

    indexing_service = IndexingService()

    indexing_service.index_url(url)

    # --------------------------------------------------
    # 2. Ask RAG
    # --------------------------------------------------

    print()
    print("[2] Asking RAG question...")
    print(f"Question: {question}")

    rag = RAGService()

    response = rag.ask(question)

    print()
    print("RESULT")
    print("=" * 60)
    print(response)
    print("=" * 60)


if __name__ == "__main__":
    main()
