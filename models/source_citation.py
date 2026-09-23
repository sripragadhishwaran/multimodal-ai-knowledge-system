"""
Source Citation Model.

Represents a verified source used by the RAG pipeline.
"""

from typing import Optional

from pydantic import BaseModel


class SourceCitation(BaseModel):
    """
    Structured citation information.
    """

    source_number: int

    source: str

    file_name: str

    document_id: str

    chunk_index: int

    chunk_length: int

    page: Optional[int] = None
