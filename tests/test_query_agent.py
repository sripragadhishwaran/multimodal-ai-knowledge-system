"""
Test Query Agent.
"""

from agents.query_agent import QueryAgent


def main():

    agent = QueryAgent()

    questions = [
        "What is LangGraph?",
        "What topics are included in the Generative AI roadmap?",
        "What does this PDF explain?",
        "Show me the diagram about AI.",
        "Compare the information in the PDF with the Generative AI roadmap image.",
    ]

    for question in questions:

        print("=" * 60)
        print(f"Question: {question}")

        result = agent.analyze(question)

        print(f"Normalized Query     : {result.normalized_query}")
        print(f"Intent               : {result.intent}")
        print(f"Requires Retrieval   : {result.requires_retrieval}")
        print(f"Preferred Content    : " f"{result.preferred_content_type}")


if __name__ == "__main__":
    main()
