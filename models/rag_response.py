"""
RAG Response Model.

Represents the final user-facing response
produced by the RAG workflow.
"""

from typing import Any

from pydantic import BaseModel, Field


class RAGResponse(BaseModel):
    """
    Structured response returned by the RAG system.
    """

    # ==================================================
    # ANSWER
    # ==================================================

    answer: str = ""

    # ==================================================
    # SOURCE INFORMATION
    # ==================================================

    image_sources: list[str] = Field(default_factory=list)

    document_sources: list[str] = Field(default_factory=list)

    web_sources: list[str] = Field(default_factory=list)

    # ==================================================
    # RETRIEVAL INFORMATION
    # ==================================================

    content_types: list[str] = Field(default_factory=list)

    source_count: int = 0

    multimodal: bool = False

    # ==================================================
    # WORKFLOW INFORMATION
    # ==================================================

    context_relevant: bool = False

    recovery_attempted: bool = False

    retrieval_attempts: int = 0

    best_score: float = float("inf")

    # ==================================================
    # CONVENIENCE
    # ==================================================

    metadata: dict[str, Any] = Field(default_factory=dict)
