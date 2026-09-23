"""
Retrieval Evaluation Test.

Evaluates retrieval quality independently from the
full RAG generation pipeline.

Checks:
- Direct factual retrieval
- Conceptual retrieval
- PDF-specific retrieval
- Image-specific retrieval
- Cross-modal retrieval
- Weak / out-of-scope queries
- MMR-selected results
"""

from retrieval.retriever import Retriever


def print_results(query: str, chunks, expected_types=None):
    print()
    print("=" * 90)
    print(f"QUERY: {query}")
    print("=" * 90)

    if not chunks:
        print("NO RESULTS")
        return

    print(f"RESULT COUNT: {len(chunks)}")

    if expected_types:
        actual_types = sorted(set(chunk.content_type for chunk in chunks))
        print(f"EXPECTED TYPES: {expected_types}")
        print(f"ACTUAL TYPES:   {actual_types}")

    print()

    for index, chunk in enumerate(chunks, start=1):

        print(f"RESULT #{index}")
        print("-" * 90)

        print(f"Distance       : {chunk.score:.4f}")
        print(f"Content Type   : {chunk.content_type}")
        print(f"Source         : {chunk.source}")
        print(f"File Name      : {chunk.file_name}")
        print(f"Document ID    : {chunk.document_id}")
        print(f"Chunk Index    : {chunk.chunk_index}")
        print(f"Chunk Length   : {chunk.chunk_length}")

        if chunk.metadata.get("page") is not None:
            print(f"Page           : {chunk.metadata.get('page')}")

        print("Content Preview:")
        print(chunk.content[:250].replace("\n", " "))

        print()


def evaluate_direct_factual(retriever: Retriever):
    """
    Test a direct factual query.
    """

    query = "What is LangGraph?"

    chunks = retriever.retrieve(
        query=query,
        top_k=3,
    )

    print_results(query, chunks)


def evaluate_conceptual(retriever: Retriever):
    """
    Test a conceptual semantic query.
    """

    query = (
        "What is the difference between "
        "Artificial Intelligence, Machine Learning, "
        "and Deep Learning?"
    )

    chunks = retriever.retrieve(
        query=query,
        top_k=3,
    )

    print_results(query, chunks)


def evaluate_pdf_specific(retriever: Retriever):
    """
    Test retrieval restricted to PDF content.
    """

    query = "What topics are explained in the PDF?"

    chunks = retriever.retrieve(
        query=query,
        top_k=3,
        content_type="pdf",
    )

    print_results(
        query,
        chunks,
        expected_types=["pdf"],
    )


def evaluate_image_specific(retriever: Retriever):
    """
    Test retrieval restricted to image content.
    """

    query = "What topics are shown in the Generative AI roadmap image?"

    chunks = retriever.retrieve(
        query=query,
        top_k=3,
        content_type="image",
    )

    print_results(
        query,
        chunks,
        expected_types=["image"],
    )


def evaluate_cross_modal(retriever: Retriever):
    """
    Test retrieval across multiple content types.
    """

    query = "What are the main topics in the Generative AI roadmap?"

    chunks = retriever.retrieve_multi_content(
        query=query,
        top_k=3,
        content_types=["image", "pdf"],
    )

    print_results(
        query,
        chunks,
        expected_types=["image", "pdf"],
    )


def evaluate_weak_query(retriever: Retriever):
    """
    Test a weak / potentially out-of-scope query.

    We do not expect a particular answer here.
    The purpose is to observe whether the retriever
    appropriately returns few or no relevant chunks.
    """

    query = "What is the population of Mars?"

    chunks = retriever.retrieve(
        query=query,
        top_k=3,
    )

    print_results(query, chunks)


def evaluate_mmr(retriever: Retriever):
    """
    Explicitly exercise MMR by requesting multiple
    semantically related results.
    """

    query = (
        "Explain the main concepts and topics " "related to Artificial Intelligence."
    )

    chunks = retriever.retrieve(
        query=query,
        top_k=5,
    )

    print_results(query, chunks)


def main():

    print()
    print("#" * 90)
    print("RETRIEVAL EVALUATION")
    print("#" * 90)

    retriever = Retriever()

    tests = [
        (
            "DIRECT FACTUAL",
            evaluate_direct_factual,
        ),
        (
            "CONCEPTUAL",
            evaluate_conceptual,
        ),
        (
            "PDF SPECIFIC",
            evaluate_pdf_specific,
        ),
        (
            "IMAGE SPECIFIC",
            evaluate_image_specific,
        ),
        (
            "CROSS MODAL",
            evaluate_cross_modal,
        ),
        (
            "WEAK / OUT OF SCOPE",
            evaluate_weak_query,
        ),
        (
            "MMR",
            evaluate_mmr,
        ),
    ]

    for name, test_function in tests:

        print()
        print("#" * 90)
        print(f"TEST: {name}")
        print("#" * 90)

        try:

            test_function(retriever)

            print()
            print(f"TEST STATUS: {name} -> SUCCESS")

        except Exception as exc:

            print()
            print(f"TEST STATUS: {name} -> FAILED")
            print(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
