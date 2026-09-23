"""
RAG Graph State.

Defines the shared state passed between
LangGraph workflow nodes.
"""

from typing import TypedDict

from models.retrieved_chunk import RetrievedChunk


class RAGState(TypedDict, total=False):

    # ==================================================
    # USER INPUT
    # ==================================================

    question: str

    # ==================================================
    # QUERY ANALYSIS
    # ==================================================

    normalized_query: str

    intent: str

    requires_retrieval: bool

    preferred_content_type: str | None

    preferred_content_types: list[str]

    retrieval_strategy: str

    # ==================================================
    # RETRIEVAL
    # ==================================================

    retrieved_chunks: list[RetrievedChunk]

    retrieval_attempts: int

    best_score: float

    # ==================================================
    # CONTEXT VALIDATION
    # ==================================================

    context_relevant: bool

    # ==================================================
    # RECOVERY
    # ==================================================

    recovery_attempted: bool

    recovery_query: str

    # ==================================================
    # MULTIMODAL INFORMATION
    # ==================================================

    content_types: list[str]

    source_count: int

    # ==================================================
    # MULTIMODAL RESPONSE
    # ==================================================

    image_sources: list[str]

    document_sources: list[str]

    web_sources: list[str]

    multimodal: bool

    # ==================================================
    # FINAL ANSWER
    # ==================================================

    answer: str
