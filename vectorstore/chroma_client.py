"""
ChromaDB Client.

Responsible for creating and managing
the ChromaDB client and collection.
"""

import chromadb
from chromadb.api.models.Collection import Collection

from config.logging_config import logger
from config.settings import settings


class ChromaClient:
    """
    Wrapper around Chroma PersistentClient.
    """

    def __init__(self):

        logger.info("Initializing ChromaDB...")

        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH
        )

        self.collection: Collection = (
            self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={
                    "description": "AI Knowledge Base"
                },
            )
        )

        logger.success(
            f"Collection '{settings.CHROMA_COLLECTION_NAME}' ready."
        )

    def get_collection(self) -> Collection:
        """
        Return active collection.
        """

        return self.collection