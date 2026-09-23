"""
Embedding Model.

Loads the Sentence Transformer model and provides
methods to generate embeddings.
"""

from sentence_transformers import SentenceTransformer

from config.logging_config import logger
from config.settings import settings


class EmbeddingModel:
    """
    Wrapper around SentenceTransformer.
    """

    def __init__(self):

        logger.info(
            f"Loading embedding model: {settings.EMBEDDING_MODEL}"
        )

        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )

        logger.success(
            "Embedding model loaded successfully."
        )

    def encode(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for a single string.
        """

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def encode_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """
        Return embedding dimension.
        """

        return self.model.get_sentence_embedding_dimension()