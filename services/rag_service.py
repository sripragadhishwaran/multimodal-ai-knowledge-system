"""
RAG Service.

Application-level service that connects
the LangGraph workflow with the response layer.
"""

from config.logging_config import logger

from graph.workflow import RAGWorkflow
from models.rag_response import RAGResponse
from response.response_builder import ResponseBuilder


class RAGService:
    """
    Main application service for the RAG system.
    """

    def __init__(
        self,
        top_k: int = 3,
    ) -> None:

        logger.info("Initializing RAG Service...")

        self.workflow = RAGWorkflow(top_k=top_k)

        logger.success("RAG Service initialized.")

    # ==================================================
    # ASK
    # ==================================================

    def ask(
        self,
        question: str,
    ) -> RAGResponse:
        """
        Process a user question through
        the complete RAG pipeline.
        """

        logger.info(f"RAG Service processing question: {question}")

        # --------------------------------------------------
        # Execute LangGraph workflow
        # --------------------------------------------------

        state = self.workflow.run(question)

        # --------------------------------------------------
        # Build final response
        # --------------------------------------------------

        response = ResponseBuilder.build(state)

        logger.success("RAG Service response built successfully.")

        return response
