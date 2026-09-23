from retrieval.retriever import Retriever


def test_content_section_filter():
    retriever = Retriever()

    chunks = retriever.retrieve(
        "What topics are explained in the PDF?",
        top_k=3,
        content_type="pdf",
        section_type="content",
    )

    assert chunks, "Expected content chunks, but got none."

    for chunk in chunks:
        assert chunk.metadata.get("section_type") == "content"


def test_reference_section_filter():
    retriever = Retriever()

    chunks = retriever.retrieve(
        "What topics are explained in the PDF?",
        top_k=3,
        content_type="pdf",
        section_type="references",
    )

    assert chunks, "Expected reference chunks, but got none."

    for chunk in chunks:
        assert chunk.metadata.get("section_type") == "references"


def test_section_metadata_survives_retrieval():
    retriever = Retriever()

    chunks = retriever.retrieve(
        "What topics are explained in the PDF?",
        top_k=3,
        content_type="pdf",
        section_type="content",
    )

    assert chunks, "Expected retrieved chunks, but got none."

    for chunk in chunks:
        assert "section_type" in chunk.metadata
        assert chunk.metadata["section_type"] == "content"
