"""
Citation-Aware Prompt Builder.

Builds grounded prompts for Retrieval-Augmented Generation
while preserving source information and multimodal metadata.
"""

from models.retrieved_chunk import RetrievedChunk


class PromptBuilder:
    """
    Builds citation-aware prompts for the LLM.
    """

    @staticmethod
    def build(
        question: str,
        chunks: list[RetrievedChunk],
    ) -> str:

        # ==================================================
        # EMPTY RETRIEVAL
        # ==================================================

        if not chunks:

            return f"""
You are a Retrieval-Augmented Generation assistant.

There is no relevant information available in the
knowledge base for this question.

You MUST NOT use general knowledge outside the
provided knowledge base.

Reply exactly with:

I don't know based on the provided knowledge.

QUESTION:
{question}

ANSWER:
""".strip()

        # ==================================================
        # DETECT CONTENT TYPES
        # ==================================================

        content_types = {chunk.content_type for chunk in chunks if chunk.content_type}

        is_image_source = "image" in content_types
        is_pdf_source = "pdf" in content_types
        is_web_source = "web" in content_types

        is_multi_content = len(content_types) > 1

        # ==================================================
        # BUILD CONTEXT
        # ==================================================

        context_parts: list[str] = []

        for index, chunk in enumerate(chunks, start=1):

            metadata = chunk.metadata or {}

            file_name = metadata.get(
                "file_name",
                chunk.file_name or "Unknown file",
            )

            page = metadata.get(
                "page",
                "N/A",
            )

            source = chunk.source or "Unknown source"

            content_type = (
                chunk.content_type or metadata.get("content_type") or "unknown"
            )

            extraction_method = (
                chunk.extraction_method
                or metadata.get("extraction_method")
                or "unknown"
            )

            context_parts.append(f"""
[Source {index}]
File: {file_name}
Source: {source}
Page: {page}
Chunk: {chunk.chunk_index}
Content Type: {content_type}
Extraction Method: {extraction_method}

Content:
{chunk.content}
""".strip())

        context = "\n\n".join(context_parts)

        # ==================================================
        # CONTENT-SPECIFIC INSTRUCTIONS
        # ==================================================

        multimodal_instructions: list[str] = []

        # --------------------------------------------------
        # IMAGE
        # --------------------------------------------------

        if is_image_source:

            multimodal_instructions.append("""
IMAGE SOURCE INSTRUCTIONS:

At least one retrieved source is an indexed image.

The image content may have been extracted using OCR
or another image extraction method.

Treat the extracted text as evidence from the indexed
image.

If the question asks about topics, labels, steps,
concepts, names, or information contained in the image,
use the extracted image content as evidence.

If the question asks to show, display, provide, or
identify the image itself, explain that the relevant
indexed image was retrieved and identify it using its
file/source information.

Do NOT invent visual information that is not present
in the supplied image evidence.
""".strip())

        # --------------------------------------------------
        # PDF
        # --------------------------------------------------

        if is_pdf_source:

            multimodal_instructions.append("""
PDF SOURCE INSTRUCTIONS:

At least one retrieved source comes from a PDF.

Use the retrieved PDF content as evidence.

Do NOT add factual information that is not supported
by the retrieved PDF content.
""".strip())

        # --------------------------------------------------
        # WEB
        # --------------------------------------------------

        if is_web_source:

            multimodal_instructions.append("""
WEB SOURCE INSTRUCTIONS:

At least one retrieved source comes from web content.

Use the retrieved web content only as evidence supplied
inside the CONTEXT.

Do NOT introduce additional facts from the internet
or from your own knowledge.
""".strip())

        # --------------------------------------------------
        # MULTI-CONTENT
        # --------------------------------------------------

        if is_multi_content:

            multimodal_instructions.append("""
MULTI-CONTENT INSTRUCTIONS:

Multiple content types were retrieved.

Use each source only for information that it actually
supports.

When comparing sources, clearly distinguish information
coming from each source.

Do NOT merge unsupported information between sources.

If one source provides only partial information,
state that limitation rather than inventing missing facts.
""".strip())

        content_specific_instructions = "\n\n".join(multimodal_instructions)

        # ==================================================
        # FINAL GROUNDED PROMPT
        # ==================================================

        prompt = f"""
You are a precise Retrieval-Augmented Generation assistant.

Your task is to answer the QUESTION using ONLY evidence
contained in the CONTEXT below.

The CONTEXT comes from the user's indexed knowledge base.

============================================================
CORE GROUNDING RULES
============================================================

1. Use ONLY the provided CONTEXT as factual evidence.

2. Carefully read ALL retrieved sources before answering.

3. A source does NOT need to contain the exact wording
   of the question to be useful.

4. Use information that directly or reasonably supports
   the question.

5. Distinguish between:
   - information explicitly stated by a source
   - information that can reasonably be inferred from
     the source.

6. Do NOT turn an inference into a fact.

7. Do NOT use outside knowledge to fill missing information.

8. Do NOT invent definitions, explanations, examples,
   names, numbers, relationships, or visual details.

9. If the retrieved context provides PARTIAL information,
   answer using the supported information and clearly
   state what the context does NOT establish.

10. Only say:

I don't know based on the provided knowledge.

when the retrieved context genuinely provides no useful
evidence for answering the question.

11. If the context provides useful related information
but does NOT provide a complete answer, give the useful
supported information instead of automatically refusing.

12. Every factual statement in the answer MUST have a
citation.

13. Use the source number assigned in the CONTEXT.

14. Citation format MUST be exactly:

[Source 1]

15. If multiple sources support a statement, cite all
relevant sources.

16. Do NOT cite a source unless it supports the statement.

17. Keep the answer concise and directly relevant.

============================================================
ANSWERING PARTIAL EVIDENCE
============================================================

If the question asks for a definition but the context
does not contain a formal definition:

- Do NOT invent a definition.
- State that the indexed knowledge base does not provide
  a direct definition.
- Then provide any directly relevant information that
  the retrieved sources actually contain.

Example:

"The indexed knowledge base does not provide a direct
definition of X. However, the retrieved source identifies
the following topics related to X: ... [Source 1]"

If the question asks for topics, steps, components,
roadmap items, labels, or concepts, list the items that
are actually present in the retrieved evidence.

If the question asks for a comparison, compare only
information supported by the retrieved sources.

If the question asks to show or provide an indexed image,
identify the retrieved image using its source/file
information. Do NOT pretend to visually display an image
when only OCR text is available.

============================================================
CONTENT-SPECIFIC INSTRUCTIONS
============================================================

{content_specific_instructions}

============================================================
CONTEXT
============================================================

{context}

============================================================
QUESTION
============================================================

{question}

============================================================
ANSWER
============================================================

Answer using ONLY the evidence above.

Every factual statement must contain the appropriate
[Source X] citation.
""".strip()

        return prompt
