"""
Recursive Character Chunker.

Creates overlapping chunks for better RAG retrieval.
"""

from models.chunk import Chunk
from models.document import Document


class RecursiveChunker:
    """
    Splits documents into overlapping chunks.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 100,
    ):

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(
        self,
        document: Document,
    ) -> list[Chunk]:

        text = document.content.strip()

        chunks: list[Chunk] = []

        start = 0

        index = 0

        while start < len(text):

            end = min(
                start + self.chunk_size,
                len(text),
            )

            chunk_text = text[start:end]

            chunks.append(
                Chunk(
    document_id=document.id,
    chunk_index=index,
    content=chunk_text,

    chunk_length=len(chunk_text),

    source=document.source,

    metadata={
        **document.metadata,
        "chunk_index": index,
    },
)
            )

            index += 1

            if end >= len(text):
                break

            start = end - self.overlap

        return chunks

    def chunk_documents(
        self,
        documents: list[Document],
    ) -> list[Chunk]:

        all_chunks: list[Chunk] = []

        for document in documents:

            all_chunks.extend(
                self.chunk_document(document)
            )

        return all_chunks