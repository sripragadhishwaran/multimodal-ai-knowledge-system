from services.rag_service import RAGService

rag = RAGService()

question = "What is Python?"

response = rag.ask(question)

print()

print("Question:")
print(response.question)

print()

print("Answer:")
print(response.answer)

print()

print("Sources:")

for source in response.sources:

    print(source.source)

print()

print("Retrieved Chunks:")
print(response.retrieved_chunks)
