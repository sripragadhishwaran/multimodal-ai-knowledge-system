"""
Retriever Layer.

Handles semantic retrieval from the vector database,
distance filtering, section-aware ranking, and MMR
diversity selection.
"""

from __future__ import annotations

from config.logging_config import logger
from models.retrieved_chunk import RetrievedChunk
from retrieval.section_policy import SectionPolicyEngine
from vectorstore.index_manager import IndexManager


class Retriever:
    """
    Retrieves relevant chunks from ChromaDB.

    Responsibilities:
    - Validate retrieval requests
    - Determine distance thresholds
    - Perform semantic search
    - Filter low-relevance candidates
    - Apply section-aware retrieval policy
    - Apply MMR diversity selection
    - Support multi-content retrieval
    """

    # ==================================================
    # CONTENT-TYPE DISTANCE THRESHOLDS
    # ==================================================

    DEFAULT_MAX_DISTANCE = 1.2

    # Retrieve more candidates than the final result count
    # so that filtering and diversity selection have room
    # to operate.
    CANDIDATE_MULTIPLIER = 3

    # MMR trade-off:
    #
    # 1.0 -> maximum relevance
    # 0.0 -> maximum diversity
    #
    # 0.7 keeps relevance dominant while reducing
    # redundant chunks.
    MMR_LAMBDA = 0.7

    CONTENT_TYPE_THRESHOLDS = {
        "text": 1.2,
        "image": 1.5,
        "pdf": 1.7,
        "web": 1.2,
    }

    def __init__(self) -> None:
        """
        Initialize the retriever.
        """

        self.section_policy = SectionPolicyEngine()
        self.index_manager = IndexManager()

    # ==================================================
    # GET DISTANCE THRESHOLD
    # ==================================================

    @classmethod
    def _get_max_distance(
        cls,
        content_type: str | None,
        max_distance: float | None,
    ) -> float:
        """
        Determine the distance threshold for retrieval.

        Explicit max_distance takes priority.

        If no explicit threshold is supplied,
        a content-type-specific threshold is used.
        """

        if max_distance is not None:

            if max_distance <= 0:

                logger.warning(
                    f"Invalid max_distance={max_distance}. "
                    f"Using default max_distance="
                    f"{cls.DEFAULT_MAX_DISTANCE}."
                )

                return cls.DEFAULT_MAX_DISTANCE

            return max_distance

        if content_type:

            threshold = cls.CONTENT_TYPE_THRESHOLDS.get(content_type.lower())

            if threshold is not None:
                return threshold

        return cls.DEFAULT_MAX_DISTANCE

    # ==================================================
    # CANDIDATE EMBEDDINGS
    # ==================================================

    def _embed_candidates(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[list[float]]:
        """
        Generate normalized embeddings for retrieved
        candidate chunks.

        The same embedding model used by the
        IndexManager is reused to keep the embedding
        space consistent with the indexed vectors.
        """

        if not chunks:
            return []

        texts = [chunk.content for chunk in chunks]

        embeddings = self.index_manager.embedding_model.encode_batch(texts)

        logger.info(
            f"Generated embeddings for " f"{len(embeddings)} candidate chunk(s)."
        )

        return embeddings

    # ==================================================
    # SECTION-AWARE POLICY
    # ==================================================

    def _apply_section_policy(
        self,
        query: str,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        """
        Apply section-aware ranking without modifying
        the original semantic distance stored in each chunk.

        Lower adjusted distance means higher retrieval
        priority.

        The original chunk.score remains the actual
        semantic distance returned by ChromaDB.
        """

        if not chunks:
            return []

        ranked_chunks: list[tuple[float, RetrievedChunk]] = []

        for chunk in chunks:

            section_type = chunk.metadata.get("section_type")

            priority = self.section_policy.get_priority(
                query=query,
                section_type=section_type,
            )

            # ChromaDB distance is lower-is-better.
            #
            # priority=1.0
            #     -> no change
            #
            # priority=0.85
            #     -> increases effective distance
            #     -> lower retrieval priority
            adjusted_distance = chunk.score / priority

            ranked_chunks.append(
                (
                    adjusted_distance,
                    chunk,
                )
            )

            logger.debug(
                f"Section policy: "
                f"section={section_type}, "
                f"original_distance="
                f"{chunk.score:.4f}, "
                f"priority={priority:.2f}, "
                f"adjusted_distance="
                f"{adjusted_distance:.4f}"
            )

        ranked_chunks.sort(key=lambda item: item[0])

        return [chunk for _, chunk in ranked_chunks]

    # ==================================================
    # MMR SELECTION
    # ==================================================

    def _apply_mmr(
        self,
        chunks: list[RetrievedChunk],
        candidate_embeddings: list[list[float]],
        query_embedding: list[float],
        top_k: int,
        query: str,
    ) -> list[RetrievedChunk]:
        """
        Select diverse and relevant chunks using
        Maximal Marginal Relevance (MMR).

        MMR balances:

            - relevance to the query
            - diversity among selected chunks
        """

        if not chunks:
            return []

        if len(chunks) != len(candidate_embeddings):

            logger.warning("MMR skipped: chunk and embedding " "counts do not match.")

            return chunks[:top_k]

        if top_k <= 0:
            return []

        if top_k >= len(chunks):
            return chunks

        if not query_embedding:

            logger.warning("MMR skipped: query embedding " "is unavailable.")

            return chunks[:top_k]

        # --------------------------------------------------
        # Query relevance scores
        # --------------------------------------------------

        relevance_scores = []

        for chunk, candidate_embedding in zip(
            chunks,
            candidate_embeddings,
        ):
            semantic_relevance = sum(
                query_value * candidate_value
                for query_value, candidate_value in zip(
                    query_embedding,
                    candidate_embedding,
                )
            )

            section_type = chunk.metadata.get("section_type")

            section_priority = self.section_policy.get_priority(
                query=query,
                section_type=section_type,
            )

            adjusted_relevance = semantic_relevance * section_priority

            relevance_scores.append(adjusted_relevance)

            logger.debug(
                f"MMR section adjustment: "
                f"section={section_type}, "
                f"semantic_relevance="
                f"{semantic_relevance:.4f}, "
                f"priority={section_priority:.2f}, "
                f"adjusted_relevance="
                f"{adjusted_relevance:.4f}"
            )

        # --------------------------------------------------
        # MMR selection
        # --------------------------------------------------

        selected_indices: list[int] = []

        remaining_indices = list(range(len(chunks)))

        while remaining_indices and len(selected_indices) < top_k:

            best_index = None
            best_mmr_score = float("-inf")

            for candidate_index in remaining_indices:

                relevance = relevance_scores[candidate_index]

                # The first selected candidate has
                # no redundancy penalty.
                if not selected_indices:

                    redundancy = 0.0

                else:

                    redundancy = max(
                        sum(
                            a * b
                            for a, b in zip(
                                candidate_embeddings[candidate_index],
                                candidate_embeddings[selected_index],
                            )
                        )
                        for selected_index in selected_indices
                    )

                mmr_score = (
                    self.MMR_LAMBDA * relevance - (1 - self.MMR_LAMBDA) * redundancy
                )

                if mmr_score > best_mmr_score:

                    best_mmr_score = mmr_score
                    best_index = candidate_index

            if best_index is None:
                break

            selected_indices.append(best_index)

            remaining_indices.remove(best_index)

            logger.info(
                f"MMR selected candidate "
                f"#{best_index + 1}: "
                f"relevance="
                f"{relevance_scores[best_index]:.4f}, "
                f"mmr="
                f"{best_mmr_score:.4f}"
            )

        return [chunks[index] for index in selected_indices]

    # ==================================================
    # RETRIEVE
    # ==================================================

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        max_distance: float | None = None,
        content_type: str | None = None,
        section_type: str | None = None,
    ) -> list[RetrievedChunk]:
        """
        Retrieve relevant chunks from ChromaDB.

        Parameters
        ----------
        query : str
            User search query.

        top_k : int
            Maximum number of retrieved chunks.

        max_distance : float | None
            Optional explicit maximum semantic distance.

            If None, the threshold is selected according
            to the content type.

        content_type : str | None
            Optional metadata filter.

            Examples:
                pdf
                image
                web
                text

        section_type : str | None
            Optional metadata filter.

            Examples:
                content
                references
        """

        # --------------------------------------------------
        # Validate query
        # --------------------------------------------------

        if not query or not query.strip():

            logger.warning("Empty query received.")

            return []

        query = query.strip()

        # --------------------------------------------------
        # Validate top_k
        # --------------------------------------------------

        if top_k <= 0:

            logger.warning(f"Invalid top_k={top_k}. " f"Using top_k=5.")

            top_k = 5

        # --------------------------------------------------
        # Determine threshold
        # --------------------------------------------------

        effective_max_distance = self._get_max_distance(
            content_type=content_type,
            max_distance=max_distance,
        )

        # --------------------------------------------------
        # Logging
        # --------------------------------------------------

        logger.info(f"Retrieving context for query: " f"{query}")

        logger.info(
            f"Retrieval settings: "
            f"top_k={top_k}, "
            f"max_distance="
            f"{effective_max_distance}, "
            f"content_type={content_type}, "
            f"section_type={section_type}"
        )

        # ==================================================
        # SEMANTIC SEARCH
        # ==================================================

        candidate_k = top_k * self.CANDIDATE_MULTIPLIER

        logger.info(
            f"Candidate pool size: " f"{candidate_k} " f"for final top_k={top_k}"
        )

        results = self.index_manager.search(
            query=query,
            top_k=candidate_k,
            content_type=content_type,
            section_type=section_type,
        )

        # ==================================================
        # PROCESS RESULTS
        # ==================================================

        return self._process_results(
            results=results,
            max_distance=effective_max_distance,
            top_k=top_k,
            query=query,
        )

    # ==================================================
    # MULTI-CONTENT RETRIEVE
    # ==================================================

    def retrieve_multi_content(
        self,
        query: str,
        top_k: int = 3,
        max_distance: float | None = None,
        content_types: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        """
        Retrieve relevant chunks from multiple
        content types.

        Example
        -------
        content_types=["image", "pdf"]

        The retriever performs a separate semantic
        search for each requested content type and
        combines the results.
        """

        # --------------------------------------------------
        # Validate query
        # --------------------------------------------------

        if not query or not query.strip():

            logger.warning("Empty query received.")

            return []

        query = query.strip()

        # --------------------------------------------------
        # Validate content types
        # --------------------------------------------------

        if not content_types:

            logger.warning("No content types supplied for " "multi-content retrieval.")

            return self.retrieve(
                query=query,
                top_k=top_k,
                max_distance=max_distance,
            )

        # --------------------------------------------------
        # Remove duplicates
        # --------------------------------------------------

        content_types = list(dict.fromkeys(content_types))

        logger.info(f"Multi-content retrieval requested: " f"{content_types}")

        all_chunks: list[RetrievedChunk] = []

        # ==================================================
        # SEARCH EACH CONTENT TYPE
        # ==================================================

        for content_type in content_types:

            logger.info(f"Searching content type: " f"{content_type}")

            chunks = self.retrieve(
                query=query,
                top_k=top_k,
                max_distance=max_distance,
                content_type=content_type,
            )

            logger.info(
                f"Retrieved {len(chunks)} "
                f"chunk(s) for content type "
                f"'{content_type}'."
            )

            all_chunks.extend(chunks)

        # ==================================================
        # NO RESULTS
        # ==================================================

        if not all_chunks:

            logger.warning("Multi-content retrieval returned " "no relevant chunks.")

            return []

        # ==================================================
        # SORT BY SCORE
        # ==================================================

        # Chroma distance is lower-is-better.
        all_chunks.sort(key=lambda chunk: chunk.score)

        # ==================================================
        # REMOVE DUPLICATES
        # ==================================================

        unique_chunks: list[RetrievedChunk] = []

        seen = set()

        for chunk in all_chunks:

            chunk_key = (
                chunk.document_id,
                chunk.chunk_index,
            )

            if chunk_key in seen:
                continue

            seen.add(chunk_key)

            unique_chunks.append(chunk)

        # ==================================================
        # LIMIT FINAL RESULTS
        # ==================================================

        final_chunks = unique_chunks[: top_k * len(content_types)]

        logger.success(
            f"Multi-content retrieval completed. "
            f"Retrieved {len(final_chunks)} "
            f"unique chunk(s) from "
            f"{len(content_types)} content type(s)."
        )

        return final_chunks

    # ==================================================
    # PROCESS RESULTS
    # ==================================================

    def _process_results(
        self,
        results: dict,
        max_distance: float,
        top_k: int,
        query: str,
    ) -> list[RetrievedChunk]:
        """
        Convert raw ChromaDB results into
        RetrievedChunk objects and apply:

        1. Distance filtering
        2. Section-aware ranking
        3. MMR diversity selection
        """

        # ==================================================
        # EXTRACT RESULTS
        # ==================================================

        documents = results.get(
            "documents",
            [[]],
        )

        distances = results.get(
            "distances",
            [[]],
        )

        metadatas = results.get(
            "metadatas",
            [[]],
        )

        query_embedding = results.get(
            "query_embedding",
            None,
        )

        documents = documents[0] if documents else []

        distances = distances[0] if distances else []

        metadatas = metadatas[0] if metadatas else []

        # ==================================================
        # NO RESULTS
        # ==================================================

        if not documents:

            logger.warning("No documents returned " "from semantic search.")

            return []

        logger.info(f"ChromaDB returned " f"{len(documents)} " f"candidate chunk(s).")

        # ==================================================
        # BUILD RETRIEVED CHUNKS
        # ==================================================

        retrieved_chunks: list[RetrievedChunk] = []

        for index, (
            document,
            distance,
            metadata,
        ) in enumerate(
            zip(
                documents,
                distances,
                metadatas,
            )
        ):

            metadata = metadata or {}

            logger.info(f"Candidate #{index + 1} " f"distance: {distance:.4f}")

            # --------------------------------------------------
            # Distance filtering
            # --------------------------------------------------

            if distance > max_distance:

                logger.info(
                    f"Discarding candidate "
                    f"#{index + 1}: "
                    f"distance {distance:.4f} "
                    f"> threshold "
                    f"{max_distance:.4f}"
                )

                continue

            # --------------------------------------------------
            # Build RetrievedChunk
            # --------------------------------------------------

            retrieved_chunk = RetrievedChunk(
                content=document,
                score=distance,
                source=metadata.get(
                    "source",
                    "unknown",
                ),
                document_id=metadata.get(
                    "document_id",
                    "unknown",
                ),
                chunk_index=int(
                    metadata.get(
                        "chunk_index",
                        0,
                    )
                ),
                chunk_length=int(
                    metadata.get(
                        "chunk_length",
                        len(document),
                    )
                ),
                metadata=metadata,
                content_type=metadata.get(
                    "content_type",
                    "unknown",
                ),
                extraction_method=metadata.get(
                    "extraction_method",
                    "unknown",
                ),
                file_name=metadata.get(
                    "file_name",
                    "unknown",
                ),
            )

            retrieved_chunks.append(retrieved_chunk)

            logger.info(
                f"Accepted candidate " f"#{index + 1}: " f"distance={distance:.4f}"
            )

        logger.success(
            f"Retrieved "
            f"{len(retrieved_chunks)} "
            f"relevant chunk(s) "
            f"after filtering."
        )

        # ==================================================
        # MMR DIVERSITY SELECTION
        # ==================================================

        if len(retrieved_chunks) <= top_k:

            final_chunks = retrieved_chunks

        else:

            if not query_embedding:

                logger.warning(
                    "Query embedding unavailable. "
                    "Falling back to "
                    "section-aware ranking."
                )

                final_chunks = retrieved_chunks[:top_k]

            else:

                candidate_embeddings = self._embed_candidates(retrieved_chunks)

                final_chunks = self._apply_mmr(
                    chunks=retrieved_chunks,
                    candidate_embeddings=candidate_embeddings,
                    query_embedding=query_embedding,
                    top_k=top_k,
                    query=query,
                )

        logger.success(
            f"Retrieved {len(final_chunks)} "
            f"final chunk(s) after MMR "
            f"selection from "
            f"{len(retrieved_chunks)} "
            f"accepted candidate(s)."
        )

        return final_chunks
