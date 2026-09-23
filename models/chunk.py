"""
Chunk model.

Represents one semantic chunk produced
from a Document.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """
    Standardized chunk model.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    document_id: str

    chunk_index: int

    content: str

    chunk_length: int

    source: str

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)