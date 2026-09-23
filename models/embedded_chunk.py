"""
Embedded Chunk Model.

Represents a document chunk together with
its vector embedding and metadata required
for storage in ChromaDB.
"""

from typing import Any

from pydantic import BaseModel, Field


class EmbeddedChunk(BaseModel):
    """
    Chunk containing its vector embedding.
    """

    id: str

    document_id: str

    chunk_index: int

    content: str

    source: str

    chunk_length: int

    embedding: list[float]

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    @property
    def chroma_metadata(self) -> dict[str, Any]:
        """
        Convert chunk information into metadata
        suitable for storage in ChromaDB.
        """

        return {
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "source": self.source,
            "chunk_length": self.chunk_length,
            **self.metadata,
        }