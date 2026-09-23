"""
RAG Workflow.

Defines the LangGraph workflow for the
Retrieval-Augmented Generation pipeline.

Workflow:

START
  ↓
analyze_query
  ↓
retrieve
  ↓
validate_context
  ↓
 ┌───────────────────────────────┐
 │                               │
relevant                    not relevant
 │                               │
 ↓                               ↓
generate                  recovery_retrieve
 │                               │
 │                               ↓
 │                         validate_context
 │                               │
 │                     ┌─────────┴─────────┐
 │                     │                   │
 │                  relevant           not relevant
 │                     │                   │
 │                     ↓                   ↓
 │                  generate            fallback
 │                     │                   │
 └──────────────┬──────┘                   │
                ↓                          │
               END ←───────────────────────┘
"""

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from config.logging_config import logger

from graph.nodes import RAGNodes
from graph.state import RAGState


class RAGWorkflow:
    """
    LangGraph-based RAG workflow.

    This class is responsible only for executing
    the internal RAG workflow and returning RAGState.

    Conversion from RAGState to RAGResponse is handled
    by the application-level RAGService.
    """

    def __init__(
        self,
        top_k: int = 3,
    ) -> None:
        """
        Initialize and compile the RAG workflow.
        """

        logger.info("Initializing LangGraph RAG workflow...")

        # ==================================================
        # INITIALIZE NODE COLLECTION
        # ==================================================

        self.nodes = RAGNodes(
            top_k=top_k,
        )

        # ==================================================
        # CREATE GRAPH
        # ==================================================

        workflow = StateGraph(RAGState)

        # ==================================================
        # REGISTER NODES
        # ==================================================

        workflow.add_node(
            "analyze_query",
            self.nodes.analyze_query,
        )

        workflow.add_node(
            "retrieve",
            self.nodes.retrieve,
        )

        workflow.add_node(
            "validate_context",
            self.nodes.validate_context,
        )

        workflow.add_node(
            "recovery_retrieve",
            self.nodes.recovery_retrieve,
        )

        workflow.add_node(
            "generate",
            self.nodes.generate,
        )

        workflow.add_node(
            "fallback",
            self.nodes.fallback,
        )

        # ==================================================
        # START → ANALYZE QUERY
        # ==================================================

        workflow.add_edge(
            START,
            "analyze_query",
        )

        # ==================================================
        # ANALYZE QUERY → RETRIEVE
        # ==================================================

        workflow.add_edge(
            "analyze_query",
            "retrieve",
        )

        # ==================================================
        # RETRIEVE → VALIDATE CONTEXT
        # ==================================================

        workflow.add_edge(
            "retrieve",
            "validate_context",
        )

        # ==================================================
        # VALIDATION ROUTING
        # ==================================================

        workflow.add_conditional_edges(
            "validate_context",
            self.route_after_validation,
            {
                "generate": "generate",
                "recovery": "recovery_retrieve",
                "fallback": "fallback",
            },
        )

        # ==================================================
        # RECOVERY → VALIDATION
        # ==================================================

        workflow.add_edge(
            "recovery_retrieve",
            "validate_context",
        )

        # ==================================================
        # GENERATE → END
        # ==================================================

        workflow.add_edge(
            "generate",
            END,
        )

        # ==================================================
        # FALLBACK → END
        # ==================================================

        workflow.add_edge(
            "fallback",
            END,
        )

        # ==================================================
        # COMPILE
        # ==================================================

        self.graph = workflow.compile()

        logger.success("LangGraph RAG workflow compiled successfully.")

    # ======================================================
    # CONDITIONAL ROUTING
    # ======================================================

    @staticmethod
    def route_after_validation(
        state: RAGState,
    ) -> str:
        """
        Decide whether to:

        1. Generate an answer
        2. Attempt recovery retrieval
        3. Use fallback
        """

        context_relevant = state.get(
            "context_relevant",
            False,
        )

        recovery_attempted = state.get(
            "recovery_attempted",
            False,
        )

        # --------------------------------------------------
        # RELEVANT CONTEXT
        # --------------------------------------------------

        if context_relevant:

            logger.info("Context is relevant. " "Routing to generate.")

            return "generate"

        # --------------------------------------------------
        # RECOVERY ALREADY ATTEMPTED
        # --------------------------------------------------

        if recovery_attempted:

            logger.warning(
                "Context is still not relevant "
                "after recovery. "
                "Routing to fallback."
            )

            return "fallback"

        # --------------------------------------------------
        # FIRST RETRIEVAL FAILED
        # --------------------------------------------------

        logger.warning("Context is not relevant. " "Routing to recovery retrieval.")

        return "recovery"

    # ======================================================
    # RUN
    # ======================================================

    def run(
        self,
        question: str,
    ) -> RAGState:
        """
        Execute the complete RAG workflow.

        Returns
        -------
        RAGState
            Final internal state produced by LangGraph.

        Important
        ---------
        This method returns RAGState only.

        RAGResponse conversion is intentionally handled
        by RAGService.
        """

        logger.info("Starting LangGraph RAG workflow...")

        # ==================================================
        # INITIAL STATE
        # ==================================================

        initial_state: RAGState = {
            # --------------------------------------------------
            # USER INPUT
            # --------------------------------------------------
            "question": question,
            # --------------------------------------------------
            # QUERY ANALYSIS
            # --------------------------------------------------
            "normalized_query": "",
            "intent": "",
            "requires_retrieval": True,
            "preferred_content_type": None,
            "preferred_content_types": [],
            "retrieval_strategy": "semantic",
            # --------------------------------------------------
            # RETRIEVAL
            # --------------------------------------------------
            "retrieved_chunks": [],
            "retrieval_attempts": 0,
            "best_score": float("inf"),
            # --------------------------------------------------
            # CONTEXT VALIDATION
            # --------------------------------------------------
            "context_relevant": False,
            # --------------------------------------------------
            # RECOVERY
            # --------------------------------------------------
            "recovery_attempted": False,
            "recovery_query": "",
            # --------------------------------------------------
            # MULTIMODAL INFORMATION
            # --------------------------------------------------
            "content_types": [],
            "source_count": 0,
            # --------------------------------------------------
            # MULTIMODAL RESPONSE
            # --------------------------------------------------
            "image_sources": [],
            "document_sources": [],
            "web_sources": [],
            "multimodal": False,
            # --------------------------------------------------
            # FINAL ANSWER
            # --------------------------------------------------
            "answer": "",
        }

        # ==================================================
        # EXECUTE GRAPH
        # ==================================================

        final_state = self.graph.invoke(initial_state)

        # ==================================================
        # COMPLETION
        # ==================================================

        logger.success("LangGraph RAG workflow completed.")

        # ==================================================
        # IMPORTANT
        # ==================================================
        #
        # Return the internal LangGraph state.
        #
        # DO NOT do:
        #
        # response = ResponseBuilder.build(final_state)
        # return response
        #
        # RAGService is responsible for converting
        # RAGState → RAGResponse.
        # ==================================================

        return final_state
