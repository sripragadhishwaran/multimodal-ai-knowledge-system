from typing import Any

from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """
    Represents a chunk retrieved from
    the multimodal knowledge base.
    """

    content: str

    score: float

    source: str

    document_id: str

    chunk_index: int

    chunk_length: int

    metadata: dict[str, Any] = Field(default_factory=dict)

    content_type: str = "unknown"

    extraction_method: str = "unknown"

    file_name: str = "unknown"
