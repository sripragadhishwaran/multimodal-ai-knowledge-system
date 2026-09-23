"""
Indexing Service.

Coordinates document scanning, loading, chunking,
embedding, and vector indexing.

Supports incremental indexing for local files
and web URLs.
"""

import re
import hashlib
from pathlib import Path

from config.logging_config import logger
from embeddings.embedding_service import EmbeddingService
from ingestion.chunker import RecursiveChunker
from ingestion.file_scanner import FileScanner
from ingestion.loader_factory import LoaderFactory
from vectorstore.index_manager import IndexManager


@staticmethod
def _normalize_url(url: str) -> str:
    """
    Normalize URLs that may accidentally contain
    Markdown link formatting.
    """

    url = url.strip()

    # Convert:
    # [https://example.com/](https://example.com/)
    # into:
    # https://example.com/

    markdown_match = re.fullmatch(
        r"\[([^\]]+)\]\(([^)]+)\)",
        url,
    )

    if markdown_match:
        url = markdown_match.group(2)

    return url.strip()


class IndexingService:
    """
    Coordinates the complete document indexing pipeline.
    """

    def __init__(self) -> None:
        """
        Initialize indexing components.
        """

        self.index_manager = IndexManager()

        self.embedding_service = EmbeddingService()

        self.chunker = RecursiveChunker()

    # ==================================================
    # FILE FINGERPRINT
    # ==================================================

    @staticmethod
    def _get_file_hash(file_path: Path) -> str:
        """
        Generate a SHA-256 fingerprint for a file.
        """

        sha256 = hashlib.sha256()

        with file_path.open("rb") as file:

            while True:

                data = file.read(1024 * 1024)

                if not data:
                    break

                sha256.update(data)

        return sha256.hexdigest()

    # ==================================================
    # URL FINGERPRINT
    # ==================================================

    @staticmethod
    def _get_url_hash(url: str) -> str:
        """
        Generate a stable fingerprint for a URL.
        """

        return hashlib.sha256(url.strip().encode("utf-8")).hexdigest()

    # ==================================================
    # INCREMENTAL FILE CHECK
    # ==================================================

    def _is_file_indexed(
        self,
        file_path: Path,
        file_hash: str,
    ) -> bool:
        """
        Check whether a file with the same source
        and content hash has already been indexed.
        """

        results = self.index_manager.collection.get(
            where={
                "$and": [
                    {"source": {"$eq": str(file_path)}},
                    {"file_hash": {"$eq": file_hash}},
                ]
            },
            limit=1,
        )

        return len(results.get("ids", [])) > 0

    # ==================================================
    # INCREMENTAL URL CHECK
    # ==================================================

    def _is_url_indexed(
        self,
        url: str,
        url_hash: str,
    ) -> bool:
        """
        Check whether a URL has already been indexed.
        """

        results = self.index_manager.collection.get(
            where={
                "$and": [
                    {"source": {"$eq": url}},
                    {"url_hash": {"$eq": url_hash}},
                ]
            },
            limit=1,
        )

        return len(results.get("ids", [])) > 0

    # ==================================================
    # MAIN FILE INDEXING PIPELINE
    # ==================================================

    def index_directory(
        self,
        directory: str,
    ) -> None:
        """
        Scan and incrementally index documents.
        """

        logger.info(f"Scanning directory: {directory}")

        files = FileScanner.scan(directory)

        files_scanned = len(files)

        files_changed = 0
        files_skipped = 0

        documents_loaded = 0
        chunks_generated = 0
        vectors_indexed = 0

        # --------------------------------------------------
        # Process each file
        # --------------------------------------------------

        for file_path in files:

            try:

                logger.info(f"Processing: {file_path.name}")

                # ------------------------------------------
                # Generate file hash
                # ------------------------------------------

                file_hash = self._get_file_hash(file_path)

                # ------------------------------------------
                # Incremental check
                # ------------------------------------------

                if self._is_file_indexed(
                    file_path,
                    file_hash,
                ):

                    logger.info(f"Skipping unchanged file: " f"{file_path.name}")

                    files_skipped += 1

                    continue

                files_changed += 1

                logger.info(f"New or modified file detected: " f"{file_path.name}")

                # ------------------------------------------
                # Delete old vectors
                # ------------------------------------------

                deleted_vectors = self.index_manager.delete_by_source(str(file_path))

                if deleted_vectors > 0:

                    logger.info(
                        f"Removed {deleted_vectors} "
                        f"stale vector(s) for "
                        f"{file_path.name}"
                    )

                # ------------------------------------------
                # Load document
                # ------------------------------------------

                loader = LoaderFactory.get_loader(str(file_path))

                documents = loader.load(str(file_path))

                # ------------------------------------------
                # Normalize loader output
                # ------------------------------------------

                if not isinstance(
                    documents,
                    list,
                ):
                    documents = [documents]

                documents_loaded += len(documents)

                logger.info(
                    f"Loaded {len(documents)} " f"document(s) from " f"{file_path.name}"
                )

                # ------------------------------------------
                # Add file hash
                # ------------------------------------------
                for document in documents:

                    # --------------------------------------------------
                    # Normalize metadata
                    # --------------------------------------------------

                    document.metadata["file_hash"] = file_hash

                    # Source
                    document.metadata.setdefault(
                        "source",
                        str(file_path),
                    )

                    # File name
                    document.metadata.setdefault(
                        "file_name",
                        file_path.name,
                    )

                    # Extension
                    document.metadata.setdefault(
                        "extension",
                        file_path.suffix.lower(),
                    )

                    # Content type
                    if not document.metadata.get("content_type"):
                        extension = file_path.suffix.lower()

                        if extension == ".pdf":
                            content_type = "pdf"

                        elif extension == ".txt":
                            content_type = "text"

                        elif extension in {
                            ".png",
                            ".jpg",
                            ".jpeg",
                            ".webp",
                        }:
                            content_type = "image"

                        else:
                            content_type = "unknown"

                        document.metadata["content_type"] = content_type

                    # Extraction method
                    document.metadata.setdefault(
                        "extraction_method",
                        "unknown",
                    )

                # ------------------------------------------
                # Chunk
                # ------------------------------------------

                chunks = self.chunker.chunk_documents(documents)

                chunks_generated += len(chunks)

                logger.info(
                    f"Generated {len(chunks)} " f"chunk(s) from " f"{file_path.name}"
                )

                if not chunks:
                    continue

                # ------------------------------------------
                # Embeddings
                # ------------------------------------------

                embedded_chunks = self.embedding_service.embed_chunks(chunks)

                # ------------------------------------------
                # ChromaDB
                # ------------------------------------------

                self.index_manager.index_chunks(embedded_chunks)

                vectors_indexed += len(embedded_chunks)

                logger.success(f"{file_path.name} " f"indexed successfully.")

            except Exception as exc:

                logger.exception(f"Failed to process " f"{file_path.name}: {exc}")

        # ==================================================
        # SUMMARY
        # ==================================================

        logger.success("=" * 50)

        logger.success("INDEXING SUMMARY")

        logger.success("=" * 50)

        logger.success(f"Files Scanned      : " f"{files_scanned}")

        logger.success(f"Files Changed      : " f"{files_changed}")

        logger.success(f"Files Skipped      : " f"{files_skipped}")

        logger.success(f"Documents Loaded   : " f"{documents_loaded}")

        logger.success(f"Chunks Generated   : " f"{chunks_generated}")

        logger.success(f"Vectors Indexed    : " f"{vectors_indexed}")

        logger.success("=" * 50)

    # ==================================================
    # WEB URL INDEXING
    # ==================================================

    def index_url(self, url: str) -> None:
        """
        Load, chunk, embed and index a web page.

        The URL is normalized before indexing so that
        equivalent URL representations do not create
        duplicate records.
        """

        from ingestion.web_loader import WebLoader

        if not url or not url.strip():
            logger.warning("Empty URL received.")
            return

        url = url.strip()

        # --------------------------------------------------
        # Normalize URL
        # --------------------------------------------------

        if url.startswith("[") and "](" in url and url.endswith(")"):
            url = url.split("](")[1][:-1]

        logger.info(f"Indexing web URL: {url}")

        try:

            # --------------------------------------------------
            # Load web page
            # --------------------------------------------------

            loader = WebLoader()

            documents = loader.load(url)

            if not documents:
                logger.warning(f"No documents extracted from URL: {url}")
                return

            logger.info(f"Loaded {len(documents)} document(s) " f"from URL.")

            # --------------------------------------------------
            # Normalize documents
            # --------------------------------------------------

            if not isinstance(documents, list):
                documents = [documents]

            # --------------------------------------------------
            # Ensure URL metadata exists
            # --------------------------------------------------

            for document in documents:

                document.metadata["source"] = url
                document.metadata["url"] = url
                document.metadata["content_type"] = "web"

            # --------------------------------------------------
            # Chunk
            # --------------------------------------------------

            chunks = self.chunker.chunk_documents(documents)

            logger.info(f"Generated {len(chunks)} chunk(s) " f"from URL.")

            if not chunks:
                logger.warning(f"No chunks generated from URL: {url}")
                return

            # --------------------------------------------------
            # Remove previous vectors for this URL
            # --------------------------------------------------

            deleted = self.index_manager.delete_by_source(url)

            if deleted > 0:
                logger.info(f"Removed {deleted} existing vector(s) " f"for URL.")

            # --------------------------------------------------
            # Generate embeddings
            # --------------------------------------------------

            embedded_chunks = self.embedding_service.embed_chunks(chunks)

            logger.info(
                f"Generated embeddings for " f"{len(embedded_chunks)} chunk(s)."
            )

            # --------------------------------------------------
            # Store in ChromaDB
            # --------------------------------------------------

            self.index_manager.index_chunks(embedded_chunks)

            logger.success(f"Web URL indexed successfully: {url}")

        except Exception as exc:

            logger.exception(f"Failed to index web URL " f"{url}: {exc}")
