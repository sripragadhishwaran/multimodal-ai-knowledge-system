"""
API Schemas.

Defines request and response models
used by the FastAPI layer.
"""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """
    Request model for the /ask endpoint.
    """

    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask the RAG system.",
    )


class AskResponse(BaseModel):
    """
    Response model returned by the /ask endpoint.
    """

    # ==================================================
    # ANSWER
    # ==================================================

    answer: str

    # ==================================================
    # SOURCES
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
    # METADATA
    # ==================================================

    metadata: dict = Field(default_factory=dict)
