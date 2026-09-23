from graph.workflow import RAGWorkflow


def main():

    workflow = RAGWorkflow(top_k=3)

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

        try:

            result = workflow.run(question)

            print()
            print("Answer:")
            print(result.get("answer"))

            print()
            print("--------------- WORKFLOW STATE ---------------")

            print(
                "Context Relevant :",
                result.get("context_relevant"),
            )

            print(
                "Recovery Attempt :",
                result.get("recovery_attempted"),
            )

            print(
                "Retrieval Count  :",
                len(result.get("retrieved_chunks", [])),
            )

            print(
                "Retrieval Attempts:",
                result.get("retrieval_attempts"),
            )

            print(
                "Best Score       :",
                result.get("best_score"),
            )

            print()
            print(
                "Content Types    :",
                result.get("content_types"),
            )

            print(
                "Source Count     :",
                result.get("source_count"),
            )

            print()
            print("--------------- SOURCE BREAKDOWN ---------------")

            print(
                "Image Sources    :",
                result.get("image_sources", []),
            )

            print(
                "Document Sources :",
                result.get("document_sources", []),
            )

            print(
                "Web Sources      :",
                result.get("web_sources", []),
            )

            print()
            print(
                "Multimodal       :",
                result.get("multimodal"),
            )

        except Exception as exc:

            print()
            print("ERROR:")
            print(type(exc).__name__, exc)

        print("=" * 60)


if __name__ == "__main__":
    main()
