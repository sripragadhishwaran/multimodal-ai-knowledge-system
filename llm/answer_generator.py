"""
Answer Generator.

Generates grounded answers using retrieved
knowledge and the configured LLM.
"""

from config.logging_config import logger
from llm.llm_client import LLMClient
from models.retrieved_chunk import RetrievedChunk
from retrieval.prompt_builder import PromptBuilder


class AnswerGenerator:
    """
    Generates answers using retrieved context.
    """

    def __init__(self) -> None:
        """
        Initialize the LLM client.
        """

        self.llm = LLMClient()

    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> str:
        """
        Generate an answer using retrieved chunks.
        """

        if not question.strip():
            logger.warning("Empty question received.")
            return "Please provide a question."

        if not chunks:
            logger.warning("No retrieved chunks available.")

            return "I don't know based on the provided knowledge."

        logger.info(f"Generating answer for: {question}")

        # Build grounded RAG prompt
        prompt = PromptBuilder.build(
            question=question,
            chunks=chunks,
        )

        logger.info("=" * 60)
        logger.info("RAG PROMPT START")
        logger.info(prompt)
        logger.info("RAG PROMPT END")
        logger.info("=" * 60)

        # Send prompt to LLM
        answer = self.llm.generate(prompt)

        logger.success("Answer generated successfully.")

        return answer.strip()
