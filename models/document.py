"""
Shared document model used across the application.

Every loader (text, image, web, PDF, etc.)
returns a Document instance.

This ensures a consistent pipeline from ingestion
to embeddings, vector storage, retrieval, and response generation.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    Standardized document representation.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique document identifier",
    )

    content: str = Field(
        ...,
        description="Main textual content extracted from the source",
    )

    source: str = Field(
        ...,
        description="Original source path or URL",
    )

    source_type: str = Field(
        ...,
        description="Source type (text, image, web, pdf, etc.)",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Document creation timestamp",
    )