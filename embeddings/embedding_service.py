"""
Embedding Service.

Converts document chunks into embedded chunks
using the configured embedding model.
"""

import hashlib

from config.logging_config import logger
from embeddings.embedding_model import EmbeddingModel
from models.chunk import Chunk
from models.embedded_chunk import EmbeddedChunk


class EmbeddingService:
    """
    Generates vector embeddings for document chunks.
    """

    def __init__(self) -> None:
        """
        Initialize the embedding model.
        """

        self.model = EmbeddingModel()

    def embed_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[EmbeddedChunk]:
        """
        Generate embeddings for all chunks.

        Parameters
        ----------
        chunks : list[Chunk]
            Document chunks to embed.

        Returns
        -------
        list[EmbeddedChunk]
            Chunks containing vector embeddings.
        """

        if not chunks:
            logger.warning("No chunks received for embedding.")
            return []

        logger.info(f"Generating embeddings for " f"{len(chunks)} chunk(s)...")

        # --------------------------------------------------
        # Step 1: Extract text from chunks
        # --------------------------------------------------

        texts = [chunk.content for chunk in chunks]

        # --------------------------------------------------
        # Step 2: Generate embeddings in batch
        # --------------------------------------------------

        embeddings = self.model.encode_batch(texts)

        # --------------------------------------------------
        # Step 3: Create EmbeddedChunk objects
        # --------------------------------------------------

        embedded_chunks: list[EmbeddedChunk] = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):

            # Stable ID based on document identity,
            # chunk position, and content.
            chunk_identity = (
                f"{chunk.document_id}:" f"{chunk.chunk_index}:" f"{chunk.content}"
            )

            stable_id = hashlib.sha256(chunk_identity.encode("utf-8")).hexdigest()

            logger.debug(f"Chunk {chunk.chunk_index} -> " f"{stable_id}")

            embedded_chunk = EmbeddedChunk(
                id=stable_id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                # NEW: Preserve source
                source=chunk.source,
                # NEW: Preserve chunk length
                chunk_length=chunk.chunk_length,
                embedding=embedding,
                metadata=chunk.metadata,
            )

            embedded_chunks.append(embedded_chunk)

        # --------------------------------------------------
        # Step 4: Log result
        # --------------------------------------------------

        logger.success(f"Successfully embedded " f"{len(embedded_chunks)} chunk(s).")

        return embedded_chunks
