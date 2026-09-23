"""
Index Manager.

Handles storing and retrieving embeddings
from ChromaDB.
"""

from config.logging_config import logger
from embeddings.embedding_model import EmbeddingModel
from models.embedded_chunk import EmbeddedChunk
from vectorstore.chroma_client import ChromaClient


class IndexManager:
    """
    Handles indexing and semantic search operations
    for ChromaDB.
    """

    def __init__(self) -> None:
        """
        Initialize ChromaDB and the embedding model.
        """

        self.client = ChromaClient()

        self.collection = self.client.get_collection()

        # Load embedding model once
        self.embedding_model = EmbeddingModel()

    # ==================================================
    # INDEXING
    # ==================================================

    def index_chunks(
        self,
        chunks: list[EmbeddedChunk],
    ) -> None:
        """
        Store embedded chunks inside ChromaDB.
        """

        if not chunks:

            logger.warning("No chunks to index.")

            return

        logger.info(f"Indexing {len(chunks)} chunk(s)...")

        self.collection.upsert(
            ids=[chunk.id for chunk in chunks],
            embeddings=[chunk.embedding for chunk in chunks],
            documents=[chunk.content for chunk in chunks],
            metadatas=[chunk.chroma_metadata for chunk in chunks],
        )

        logger.success(f"Successfully upserted " f"{len(chunks)} chunk(s).")

    # ==================================================
    # COUNT
    # ==================================================

    def count(self) -> int:
        """
        Return the number of indexed vectors.
        """

        return self.collection.count()

    # ==================================================
    # SEARCH
    # ==================================================

    def search(
        self,
        query: str,
        top_k: int = 5,
        content_type: str | None = None,
        section_type: str | None = None,
        
    ):
        """
        Perform semantic search with optional metadata filtering.

        Parameters
        ----------
        query : str
            Search query.

        top_k : int
            Maximum number of results.

        content_type : str | None
            Optional content-type metadata filter.

            Examples:
                image
                pdf
                web
                text

        section_type : str | None
            Optional section-type metadata filter.

            Examples:
                content
                references

        Returns
        -------
        dict
            ChromaDB search results.
        """

        # --------------------------------------------------
        # Validate query
        # --------------------------------------------------

        if not query or not query.strip():

            logger.warning("Empty search query.")

            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

        query = query.strip()

        # --------------------------------------------------
        # Validate top_k
        # --------------------------------------------------

        if top_k <= 0:

            logger.warning(f"Invalid top_k={top_k}. " f"Using top_k=5.")

            top_k = 5

        logger.info(f"Searching for: {query}")

        # --------------------------------------------------
        # Generate query embedding
        # --------------------------------------------------

        query_embedding = self.embedding_model.encode(query)

        # --------------------------------------------------
        # Build ChromaDB query arguments
        # --------------------------------------------------

        query_args = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": [
                "documents",
                "metadatas",
                "distances",
            ],
        }

        # --------------------------------------------------
        # Build metadata filters
        # --------------------------------------------------

        metadata_filters = []

        if content_type:

            logger.info(f"Filtering by content_type={content_type}")

            metadata_filters.append(
                {
                    "content_type": {
                        "$eq": content_type,
                    }
                }
            )

        if section_type:

            logger.info(f"Filtering by section_type={section_type}")

            metadata_filters.append(
                {
                    "section_type": {
                        "$eq": section_type,
                    }
                }
            )

        # --------------------------------------------------
        # Apply metadata filters
        # --------------------------------------------------

        if len(metadata_filters) == 1:

            query_args["where"] = metadata_filters[0]

        elif len(metadata_filters) > 1:

            query_args["where"] = {
                "$and": metadata_filters,
            }

        # --------------------------------------------------
        # Search ChromaDB
        # --------------------------------------------------

        results = self.collection.query(**query_args)

        results["query_embedding"] = query_embedding

        logger.success("Semantic search completed.")

        return results

    # ==================================================
    # DELETE BY SOURCE
    # ==================================================

    def delete_by_source(self, source: str) -> int:
        """
        Delete all vectors belonging to a specific source.

        Parameters
        ----------
        source : str
            Original source path of the indexed file.

        Returns
        -------
        int
            Number of vectors deleted.
        """

        logger.info(f"Deleting existing vectors for: {source}")

        results = self.collection.get(
            where={"source": {"$eq": source}},
            include=["metadatas"],
        )

        ids = results.get("ids", [])

        # No existing vectors
        if not ids:

            logger.info(f"No existing vectors found for source: {source}")

            return 0

        # Delete existing vectors
        self.collection.delete(ids=ids)

        deleted_count = len(ids)

        logger.success(f"Deleted {deleted_count} vector(s) " f"for source: {source}")

        return deleted_count

    # ==================================================
    # RESET COLLECTION
    # ==================================================

    def reset_collection(self) -> None:
        """
        Delete and recreate the collection.

        Useful during development.
        """

        logger.warning(f"Resetting collection " f"'{self.collection.name}'...")

        self.client.client.delete_collection(name=self.collection.name)

        self.collection = self.client.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"description": "AI Knowledge Base"},
        )

        logger.success("Collection reset successfully.")
