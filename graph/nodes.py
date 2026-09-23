"""
LangGraph RAG Nodes.

Contains the individual nodes used by the
LangGraph Retrieval-Augmented Generation workflow.
"""

from config.logging_config import logger

from agents.query_agent import QueryAgent
from graph.state import RAGState
from llm.answer_generator import AnswerGenerator
from retrieval.retrieval_service import RetrievalService


class RAGNodes:
    """
    Collection of nodes used by the LangGraph RAG workflow.
    """

    def __init__(
        self,
        top_k: int = 3,
    ) -> None:

        logger.info("Initializing RAG Nodes...")

        self.top_k = top_k

        self.query_agent = QueryAgent()

        self.retrieval_service = RetrievalService()

        self.answer_generator = AnswerGenerator()

        logger.success("RAG Nodes initialized.")

    # ==================================================
    # ANALYZE QUERY
    # ==================================================

    def analyze_query(
        self,
        state: RAGState,
    ) -> RAGState:
        """
        Analyze the user's question and determine
        the retrieval strategy.
        """

        logger.info("LangGraph node: analyze_query")

        question = state.get(
            "question",
            "",
        )

        # --------------------------------------------------
        # Validate question
        # --------------------------------------------------

        if not isinstance(question, str):

            logger.warning(
                f"Expected question to be str, " f"received {type(question).__name__}."
            )

            question = ""

            state["question"] = ""

        # --------------------------------------------------
        # Query analysis
        # --------------------------------------------------

        analysis = self.query_agent.analyze(question)

        # --------------------------------------------------
        # Store analysis in graph state
        # --------------------------------------------------

        state["normalized_query"] = analysis.normalized_query

        state["intent"] = analysis.intent

        state["requires_retrieval"] = analysis.requires_retrieval

        state["preferred_content_type"] = analysis.preferred_content_type

        state["preferred_content_types"] = analysis.preferred_content_types or []

        state["retrieval_strategy"] = analysis.retrieval_strategy

        # --------------------------------------------------
        # Logging
        # --------------------------------------------------

        logger.success("Query analysis completed.")

        logger.info(f"Intent: {analysis.intent}")

        logger.info(f"Requires retrieval: " f"{analysis.requires_retrieval}")

        logger.info(f"Normalized query: " f"{analysis.normalized_query}")

        logger.info(f"Preferred content type: " f"{analysis.preferred_content_type}")

        logger.info(f"Preferred content types: " f"{analysis.preferred_content_types}")

        logger.info(f"Retrieval strategy: " f"{analysis.retrieval_strategy}")

        return state

    # ==================================================
    # RETRIEVE
    # ==================================================

    def retrieve(
        self,
        state: RAGState,
    ) -> RAGState:
        """
        Retrieve relevant knowledge from the vector database.
        """

        current_attempts = state.get(
            "retrieval_attempts",
            0,
        )

        attempt = current_attempts + 1

        logger.info(f"LangGraph node: retrieve " f"(attempt {attempt})")

        # --------------------------------------------------
        # Read query
        # --------------------------------------------------

        normalized_query = state.get(
            "normalized_query",
            "",
        )

        question = state.get(
            "question",
            "",
        )

        query = normalized_query or question

        if not isinstance(query, str):
            query = ""

        logger.info(f"Using retrieval query: {query}")

        # --------------------------------------------------
        # Read retrieval strategy
        # --------------------------------------------------

        retrieval_strategy = state.get(
            "retrieval_strategy",
            "semantic",
        )

        preferred_content_type = state.get(
            "preferred_content_type",
            None,
        )

        preferred_content_types = state.get(
            "preferred_content_types",
            [],
        )

        logger.info(f"Retrieval strategy: " f"{retrieval_strategy}")

        logger.info(f"Preferred content type: " f"{preferred_content_type}")

        logger.info(f"Preferred content types: " f"{preferred_content_types}")

        # ==================================================
        # PERFORM RETRIEVAL
        # ==================================================

        if retrieval_strategy == "multi_content":

            logger.info("Using multi-content retrieval.")

            retrieved_chunks = self.retrieval_service.search(
                question=query,
                top_k=self.top_k,
                content_types=preferred_content_types,
            )

        elif retrieval_strategy == "content_filtered":

            logger.info("Using content-filtered retrieval.")

            retrieved_chunks = self.retrieval_service.search(
                question=query,
                top_k=self.top_k,
                content_type=preferred_content_type,
            )

        else:

            logger.info("Using semantic retrieval.")

            retrieved_chunks = self.retrieval_service.search(
                question=query,
                top_k=self.top_k,
            )

        # ==================================================
        # UPDATE RETRIEVAL STATE
        # ==================================================

        self._update_retrieval_state(
            state=state,
            retrieved_chunks=retrieved_chunks,
            attempt=attempt,
        )

        logger.info(f"LangGraph retrieved " f"{len(retrieved_chunks)} chunk(s).")

        return state

    # ==================================================
    # VALIDATE CONTEXT
    # ==================================================

    def validate_context(
        self,
        state: RAGState,
    ) -> RAGState:
        """
        Determine whether retrieved context is
        sufficiently relevant.

        Validation is content-aware:

            semantic/text -> 1.2
            image         -> 1.5
            pdf           -> 1.7
            web           -> 1.5

        Lower Chroma distance means better relevance.
        """

        logger.info("LangGraph node: validate_context")

        retrieved_chunks = state.get(
            "retrieved_chunks",
            [],
        )

        # --------------------------------------------------
        # No chunks
        # --------------------------------------------------

        if not retrieved_chunks:

            logger.warning("Context validation failed: " "no chunks retrieved.")

            state["context_relevant"] = False

            return state

        # --------------------------------------------------
        # Determine best score
        # --------------------------------------------------

        best_score = min(chunk.score for chunk in retrieved_chunks)

        # --------------------------------------------------
        # Determine content types
        # --------------------------------------------------

        content_types = {
            (chunk.content_type or "").lower() for chunk in retrieved_chunks
        }

        # --------------------------------------------------
        # Content-aware threshold
        # --------------------------------------------------

        thresholds = {
            "image": 1.5,
            "pdf": 1.7,
            "web": 1.5,
            "text": 1.2,
        }

        # --------------------------------------------------
        # Find appropriate threshold
        # --------------------------------------------------

        if "pdf" in content_types:

            relevance_threshold = 1.7

        elif "image" in content_types:

            relevance_threshold = 1.5

        elif "web" in content_types:

            relevance_threshold = 1.5

        else:

            relevance_threshold = 1.2

        # --------------------------------------------------
        # Special handling for multi-content retrieval
        # --------------------------------------------------

        if len(content_types) > 1:

            relevant_thresholds = [
                thresholds.get(
                    content_type,
                    1.2,
                )
                for content_type in content_types
            ]

            relevance_threshold = max(relevant_thresholds)

        # --------------------------------------------------
        # Validate
        # --------------------------------------------------

        context_relevant = best_score <= relevance_threshold

        state["context_relevant"] = context_relevant

        # --------------------------------------------------
        # Logging
        # --------------------------------------------------

        if context_relevant:

            logger.success(
                f"Context validation passed with "
                f"{len(retrieved_chunks)} chunk(s). "
                f"Best score={best_score:.4f}, "
                f"threshold={relevance_threshold:.4f}"
            )

        else:

            logger.warning(
                f"Context validation failed. "
                f"Best score={best_score:.4f}, "
                f"threshold={relevance_threshold:.4f}, "
                f"content_types={sorted(content_types)}"
            )

        return state

    # ==================================================
    # RECOVERY RETRIEVE
    # ==================================================

    def recovery_retrieve(
        self,
        state: RAGState,
    ) -> RAGState:
        """
        Perform a second retrieval attempt.

        Recovery respects the original retrieval strategy.

        This prevents a failed image search from suddenly
        becoming a PDF/text search and losing the user's
        requested content type.
        """

        logger.warning("LangGraph node: recovery_retrieve")

        # --------------------------------------------------
        # Mark recovery
        # --------------------------------------------------

        state["recovery_attempted"] = True

        # --------------------------------------------------
        # Original query
        # --------------------------------------------------

        recovery_query = state.get(
            "normalized_query",
            "",
        )

        if not recovery_query:

            recovery_query = state.get(
                "question",
                "",
            )

        if not isinstance(
            recovery_query,
            str,
        ):

            recovery_query = ""

        recovery_query = recovery_query.strip()

        state["recovery_query"] = recovery_query

        logger.info(f"Recovery query: " f"{recovery_query}")

        # --------------------------------------------------
        # Read original retrieval strategy
        # --------------------------------------------------

        retrieval_strategy = state.get(
            "retrieval_strategy",
            "semantic",
        )

        preferred_content_type = state.get(
            "preferred_content_type",
            None,
        )

        preferred_content_types = state.get(
            "preferred_content_types",
            [],
        )

        logger.info(f"Recovery strategy: " f"{retrieval_strategy}")

        logger.info(f"Recovery preferred content type: " f"{preferred_content_type}")

        logger.info(f"Recovery preferred content types: " f"{preferred_content_types}")

        # ==================================================
        # CONTENT-AWARE RECOVERY
        # ==================================================

        if retrieval_strategy == "multi_content":

            logger.info("Recovery using multi-content retrieval.")

            retrieved_chunks = self.retrieval_service.search(
                question=recovery_query,
                top_k=self.top_k,
                content_types=preferred_content_types,
            )

        elif retrieval_strategy == "content_filtered":

            logger.info("Recovery using content-filtered retrieval.")

            retrieved_chunks = self.retrieval_service.search(
                question=recovery_query,
                top_k=self.top_k,
                content_type=preferred_content_type,
            )

        else:

            logger.info("Recovery using semantic retrieval.")

            retrieved_chunks = self.retrieval_service.search(
                question=recovery_query,
                top_k=self.top_k,
            )

        # ==================================================
        # IMPORTANT IMAGE PROTECTION
        # ==================================================

        original_chunks = state.get(
            "retrieved_chunks",
            [],
        )

        original_content_types = {
            (chunk.content_type or "").lower() for chunk in original_chunks
        }

        # --------------------------------------------------
        # If the original request specifically targeted
        # images and recovery finds nothing, preserve the
        # original image evidence.
        # --------------------------------------------------

        if not retrieved_chunks and "image" in original_content_types:

            logger.warning(
                "Recovery found no new chunks. " "Preserving original image retrieval."
            )

            retrieved_chunks = original_chunks

        # ==================================================
        # UPDATE STATE
        # ==================================================

        current_attempts = state.get(
            "retrieval_attempts",
            0,
        )

        attempt = current_attempts + 1

        self._update_retrieval_state(
            state=state,
            retrieved_chunks=retrieved_chunks,
            attempt=attempt,
        )

        logger.info(f"Recovery retrieved " f"{len(retrieved_chunks)} chunk(s).")

        if retrieved_chunks:

            logger.info(
                f"Recovery best score: " f"{state.get('best_score', float('inf')):.4f}"
            )

        return state

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(
        self,
        state: RAGState,
    ) -> RAGState:
        """
        Generate a grounded answer from retrieved context.
        """

        logger.info("LangGraph node: generate")

        question = state.get(
            "normalized_query",
            "",
        )

        if not question:

            question = state.get(
                "question",
                "",
            )

        if not isinstance(
            question,
            str,
        ):

            question = ""

        retrieved_chunks = state.get(
            "retrieved_chunks",
            [],
        )

        answer = self.answer_generator.generate(
            question=question,
            chunks=retrieved_chunks,
        )

        state["answer"] = answer

        logger.success("Answer generation completed.")

        return state

    # ==================================================
    # FALLBACK
    # ==================================================

    def fallback(
        self,
        state: RAGState,
    ) -> RAGState:
        """
        Return a safe fallback answer when
        retrieval cannot provide sufficient context.
        """

        logger.warning("LangGraph node: fallback")

        state["answer"] = "I don't know based on the provided knowledge."

        logger.info("Fallback answer generated.")

        return state

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================

    @staticmethod
    def _update_retrieval_state(
        state: RAGState,
        retrieved_chunks,
        attempt: int,
    ) -> None:
        """
        Update all retrieval-related fields in the
        shared LangGraph state.

        Keeps retrieve() and recovery_retrieve()
        consistent.
        """

        # --------------------------------------------------
        # Best score
        # --------------------------------------------------

        if retrieved_chunks:

            best_score = min(chunk.score for chunk in retrieved_chunks)

        else:

            best_score = float("inf")

        # --------------------------------------------------
        # Content types
        # --------------------------------------------------

        content_types = sorted(
            {
                chunk.content_type
                for chunk in retrieved_chunks
                if (chunk.content_type and chunk.content_type != "unknown")
            }
        )

        # --------------------------------------------------
        # Source count
        # --------------------------------------------------

        source_count = len({chunk.source for chunk in retrieved_chunks if chunk.source})

        # ==================================================
        # MULTIMODAL SOURCE BREAKDOWN
        # ==================================================

        image_sources: list[str] = []

        document_sources: list[str] = []

        web_sources: list[str] = []

        for chunk in retrieved_chunks:

            content_type = (chunk.content_type or "").lower()

            source = chunk.source or chunk.file_name or "unknown"

            if content_type == "image":

                image_sources.append(source)

            elif content_type in {
                "pdf",
                "text",
            }:

                document_sources.append(source)

            elif content_type == "web":

                web_sources.append(source)

        # --------------------------------------------------
        # Remove duplicates
        # --------------------------------------------------

        image_sources = list(dict.fromkeys(image_sources))

        document_sources = list(dict.fromkeys(document_sources))

        web_sources = list(dict.fromkeys(web_sources))

        # --------------------------------------------------
        # Multimodal flag
        # --------------------------------------------------

        multimodal = len(content_types) > 1

        # ==================================================
        # UPDATE STATE
        # ==================================================

        state["retrieved_chunks"] = retrieved_chunks

        state["retrieval_attempts"] = attempt

        state["best_score"] = best_score

        state["content_types"] = content_types

        state["source_count"] = source_count

        state["image_sources"] = image_sources

        state["document_sources"] = document_sources

        state["web_sources"] = web_sources

        state["multimodal"] = multimodal

        # --------------------------------------------------
        # Logging
        # --------------------------------------------------

        if retrieved_chunks:

            logger.info(f"Best retrieval score: " f"{best_score:.4f}")

        else:

            logger.info("No retrieval score available.")

        logger.info(f"Retrieved content types: " f"{content_types}")

        logger.info(f"Retrieved source count: " f"{source_count}")

        logger.info(f"Image sources: " f"{image_sources}")

        logger.info(f"Document sources: " f"{document_sources}")

        logger.info(f"Web sources: " f"{web_sources}")

        logger.info(f"Multimodal: " f"{multimodal}")
