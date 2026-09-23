"""
Retrieval Service.

Provides a clean interface for retrieving
knowledge from the vector database.
"""

from config.logging_config import logger
from models.retrieved_chunk import RetrievedChunk
from retrieval.retriever import Retriever


class RetrievalService:
    """
    Service responsible for semantic retrieval.
    """

    def __init__(self) -> None:

        self.retriever = Retriever()

    # ==================================================
    # SEARCH
    # ==================================================

    def search(
        self,
        question: str,
        top_k: int = 3,
        content_type: str | None = None,
        content_types: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        """
        Retrieve the most relevant chunks for a user question.

        Parameters
        ----------
        question : str
            User query.

        top_k : int
            Number of chunks to retrieve.

        content_type : str | None
            Single content-type filter.

            Examples:
                image
                pdf
                web
                text

        content_types : list[str] | None
            Multiple content-type filters.

            Example:
                ["image", "pdf"]

            This is used by the multi-content retrieval
            strategy.

        Returns
        -------
        list[RetrievedChunk]
            Retrieved chunks ordered by similarity.
        """

        logger.info(f"Searching knowledge base for: {question}")

        logger.info(f"Retrieval content type: {content_type}")

        logger.info(f"Retrieval content types: {content_types}")

        # ==================================================
        # MULTI-CONTENT RETRIEVAL
        # ==================================================

        if content_types:

            chunks = self.retriever.retrieve_multi_content(
                query=question,
                top_k=top_k,
                content_types=content_types,
            )

        # ==================================================
        # SINGLE CONTENT TYPE RETRIEVAL
        # ==================================================

        else:

            chunks = self.retriever.retrieve(
                query=question,
                top_k=top_k,
                content_type=content_type,
            )

        logger.success(f"Retrieved {len(chunks)} relevant chunk(s).")

        return chunks
