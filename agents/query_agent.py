"""
Query Agent.

Analyzes the user's question and determines
the appropriate retrieval strategy.

The agent also performs lightweight deterministic
query normalization and expansion to improve
semantic retrieval quality.
"""

from dataclasses import dataclass
from typing import Optional

from config.logging_config import logger


@dataclass
class QueryAnalysis:
    """
    Structured result produced by the Query Agent.
    """

    # ==================================================
    # ORIGINAL QUERY
    # ==================================================

    original_query: str

    # ==================================================
    # NORMALIZED QUERY
    # ==================================================

    normalized_query: str

    # ==================================================
    # INTENT
    # ==================================================

    intent: str

    requires_retrieval: bool

    # ==================================================
    # CONTENT TYPE
    # ==================================================

    preferred_content_type: Optional[str] = None

    preferred_content_types: list[str] | None = None

    # ==================================================
    # RETRIEVAL STRATEGY
    # ==================================================

    retrieval_strategy: str = "semantic"


class QueryAgent:
    """
    Analyzes user queries before retrieval.

    Responsibilities
    ----------------
    1. Validate the question.
    2. Normalize the query.
    3. Expand common domain abbreviations.
    4. Determine the intent.
    5. Determine whether retrieval is required.
    6. Detect preferred content types.
    7. Select the retrieval strategy.

    The agent currently uses deterministic rules.
    """

    def __init__(self) -> None:

        logger.info("Initializing Query Agent...")

        logger.success("Query Agent initialized.")

    # ==================================================
    # ANALYZE QUERY
    # ==================================================

    def analyze(
        self,
        question: str,
    ) -> QueryAnalysis:
        """
        Analyze a user question.

        Parameters
        ----------
        question : str
            User's question.

        Returns
        -------
        QueryAnalysis
            Structured query analysis.
        """

        logger.info("Query Agent analyzing question...")

        # ==================================================
        # VALIDATE INPUT
        # ==================================================

        if not question or not question.strip():

            logger.warning("Query Agent received an empty question.")

            return QueryAnalysis(
                original_query=question,
                normalized_query="",
                intent="invalid",
                requires_retrieval=False,
                preferred_content_type=None,
                preferred_content_types=[],
                retrieval_strategy="none",
            )

        # ==================================================
        # BASIC NORMALIZATION
        # ==================================================

        normalized_query = " ".join(question.strip().split())

        logger.info(f"Initial normalized query: {normalized_query}")

        # ==================================================
        # QUERY EXPANSION
        # ==================================================

        normalized_query = self._expand_query(normalized_query)

        logger.info(f"Expanded retrieval query: {normalized_query}")

        # ==================================================
        # INTENT
        # ==================================================

        intent = self._detect_intent(normalized_query)

        # ==================================================
        # RETRIEVAL REQUIREMENT
        # ==================================================

        requires_retrieval = True

        # ==================================================
        # DETECT CONTENT TYPES
        # ==================================================

        preferred_content_types = self._detect_content_types(normalized_query)

        # ==================================================
        # BACKWARD COMPATIBILITY
        # ==================================================

        preferred_content_type = (
            preferred_content_types[0] if preferred_content_types else None
        )

        # ==================================================
        # RETRIEVAL STRATEGY
        # ==================================================

        retrieval_strategy = self._determine_retrieval_strategy(preferred_content_types)

        # ==================================================
        # BUILD ANALYSIS
        # ==================================================

        analysis = QueryAnalysis(
            original_query=question,
            normalized_query=normalized_query,
            intent=intent,
            requires_retrieval=requires_retrieval,
            preferred_content_type=preferred_content_type,
            preferred_content_types=preferred_content_types,
            retrieval_strategy=retrieval_strategy,
        )

        # ==================================================
        # LOGGING
        # ==================================================

        logger.success("Query analysis completed.")

        logger.info(f"Intent: {analysis.intent}")

        logger.info(f"Requires retrieval: " f"{analysis.requires_retrieval}")

        logger.info(f"Normalized query: " f"{analysis.normalized_query}")

        logger.info(f"Preferred content types: " f"{analysis.preferred_content_types}")

        logger.info(f"Retrieval strategy: " f"{analysis.retrieval_strategy}")

        return analysis

    # ==================================================
    # QUERY EXPANSION
    # ==================================================

    @staticmethod
    def _expand_query(
        query: str,
    ) -> str:
        """
        Expand common abbreviations and informal
        terminology without changing the user's
        original question.

        This expanded query is used for retrieval.

        Examples
        --------
        "what gen ai"
            ->
        "what generative ai"

        "gen ai roadmap"
            ->
        "generative ai roadmap"

        "what ml"
            ->
        "what machine learning"
        """

        words = query.split()

        expanded_words: list[str] = []

        index = 0

        while index < len(words):

            current = words[index]

            current_lower = current.lower()

            # ==================================================
            # GENERATIVE AI
            # ==================================================

            if (
                current_lower == "gen"
                and index + 1 < len(words)
                and words[index + 1].lower() == "ai"
            ):

                expanded_words.append("generative")

                expanded_words.append(words[index + 1])

                index += 2

                continue

            # ==================================================
            # MACHINE LEARNING
            # ==================================================

            if current_lower == "ml":

                expanded_words.append("machine")

                expanded_words.append("learning")

                index += 1

                continue

            # ==================================================
            # DEEP LEARNING
            # ==================================================

            if current_lower == "dl":

                expanded_words.append("deep")

                expanded_words.append("learning")

                index += 1

                continue

            # ==================================================
            # NATURAL LANGUAGE PROCESSING
            # ==================================================

            if current_lower == "nlp":

                expanded_words.append("natural")

                expanded_words.append("language")

                expanded_words.append("processing")

                index += 1

                continue

            # ==================================================
            # LARGE LANGUAGE MODEL
            # ==================================================

            if current_lower == "llm" or current_lower == "llms":

                expanded_words.append("large")

                expanded_words.append("language")

                expanded_words.append("model")

                index += 1

                continue

            # ==================================================
            # RETAIN ORIGINAL WORD
            # ==================================================

            expanded_words.append(current)

            index += 1

        return " ".join(expanded_words)

    # ==================================================
    # CONTENT TYPE DETECTION
    # ==================================================

    @staticmethod
    def _detect_content_types(
        query: str,
    ) -> list[str]:
        """
        Detect all content types suggested by the query.

        Returns
        -------
        list[str]
            Detected content types.
        """

        query_lower = query.lower()

        detected_types: list[str] = []

        # ==================================================
        # IMAGE
        # ==================================================

        image_keywords = (
            "image",
            "picture",
            "photo",
            "diagram",
            "figure",
            "roadmap",
            "chart",
        )

        if any(keyword in query_lower for keyword in image_keywords):

            detected_types.append("image")

        # ==================================================
        # PDF
        # ==================================================

        pdf_keywords = (
            "pdf",
            "document",
            "report",
            "paper",
        )

        if any(keyword in query_lower for keyword in pdf_keywords):

            detected_types.append("pdf")

        # ==================================================
        # WEB
        # ==================================================

        web_keywords = (
            "website",
            "web page",
            "url",
            "web",
            "online",
        )

        if any(keyword in query_lower for keyword in web_keywords):

            detected_types.append("web")

        # ==================================================
        # TEXT
        # ==================================================

        text_keywords = (
            "text file",
            "text document",
        )

        if any(keyword in query_lower for keyword in text_keywords):

            detected_types.append("text")

        return detected_types

    # ==================================================
    # RETRIEVAL STRATEGY
    # ==================================================

    @staticmethod
    def _determine_retrieval_strategy(
        preferred_content_types: list[str],
    ) -> str:
        """
        Determine how the retrieval layer should search.

        Returns
        -------
        str

            semantic
                Search across the complete knowledge base.

            content_filtered
                Search restricted to one content type.

            multi_content
                Search across multiple specified
                content types.

            none
                No retrieval required.
        """

        # ==================================================
        # NO CONTENT TYPE
        # ==================================================

        if not preferred_content_types:

            return "semantic"

        # ==================================================
        # MULTIPLE CONTENT TYPES
        # ==================================================

        if len(preferred_content_types) > 1:

            return "multi_content"

        # ==================================================
        # SINGLE CONTENT TYPE
        # ==================================================

        return "content_filtered"

    # ==================================================
    # INTENT DETECTION
    # ==================================================

    @staticmethod
    def _detect_intent(
        query: str,
    ) -> str:
        """
        Detect the primary intent of the user query.
        """

        query_lower = query.lower()

        # ==================================================
        # COMPARISON
        # ==================================================

        comparison_keywords = (
            "compare",
            "comparison",
            "difference",
            "differences",
            "different from",
            "similar",
            "similarities",
            "versus",
            "vs",
        )

        if any(keyword in query_lower for keyword in comparison_keywords):

            return "comparison_query"

        # ==================================================
        # KNOWLEDGE
        # ==================================================

        return "knowledge_query"
