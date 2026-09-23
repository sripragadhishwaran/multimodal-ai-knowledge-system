"""
Response Builder.

Converts the internal LangGraph RAG state
into a clean structured response.
"""

from graph.state import RAGState
from models.rag_response import RAGResponse


class ResponseBuilder:
    """
    Builds the final user-facing RAG response.
    """

    @staticmethod
    def build(
        state: RAGState,
    ) -> RAGResponse:
        """
        Convert LangGraph state into RAGResponse.
        """

        return RAGResponse(
            # ==================================================
            # ANSWER
            # ==================================================
            answer=state.get(
                "answer",
                "",
            ),
            # ==================================================
            # SOURCES
            # ==================================================
            image_sources=state.get(
                "image_sources",
                [],
            ),
            document_sources=state.get(
                "document_sources",
                [],
            ),
            web_sources=state.get(
                "web_sources",
                [],
            ),
            # ==================================================
            # RETRIEVAL
            # ==================================================
            content_types=state.get(
                "content_types",
                [],
            ),
            source_count=state.get(
                "source_count",
                0,
            ),
            multimodal=state.get(
                "multimodal",
                False,
            ),
            # ==================================================
            # WORKFLOW
            # ==================================================
            context_relevant=state.get(
                "context_relevant",
                False,
            ),
            recovery_attempted=state.get(
                "recovery_attempted",
                False,
            ),
            retrieval_attempts=state.get(
                "retrieval_attempts",
                0,
            ),
            best_score=state.get(
                "best_score",
                float("inf"),
            ),
            # ==================================================
            # METADATA
            # ==================================================
            metadata={
                "intent": state.get(
                    "intent",
                    "",
                ),
                "retrieval_strategy": state.get(
                    "retrieval_strategy",
                    "semantic",
                ),
                "preferred_content_types": state.get(
                    "preferred_content_types",
                    [],
                ),
            },
        )
