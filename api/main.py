"""
FastAPI Application.

Exposes the multimodal RAG system
through HTTP endpoints.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.schemas import (
    AskRequest,
    AskResponse,
)

from config.logging_config import logger

from services.rag_service import RAGService
from services.indexing_service import IndexingService

# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_ROOT = BASE_DIR / "data" / "raw"


# ==================================================
# APPLICATION
# ==================================================

app = FastAPI(
    title="Multimodal AI Knowledge System",
    description=(
        "Multimodal Retrieval-Augmented Generation "
        "API powered by LangGraph, ChromaDB and Gemini."
    ),
    version="1.0.0",
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=[
        "*",
    ],
    allow_headers=[
        "*",
    ],
)


# ==================================================
# SOURCE FILES
# ==================================================

if DATA_ROOT.exists():

    app.mount(
        "/sources",
        StaticFiles(directory=str(DATA_ROOT)),
        name="sources",
    )

    logger.info(f"Source files mounted from: {DATA_ROOT}")

else:

    logger.warning(f"Source directory does not exist: {DATA_ROOT}")


# ==================================================
# SERVICES
# ==================================================

rag_service = RAGService(top_k=3)

indexing_service = IndexingService()


# ==================================================
# HEALTH CHECK
# ==================================================


@app.get(
    "/health",
    tags=["System"],
)
def health_check():
    """
    Check whether the API is running.
    """

    return {
        "status": "ok",
        "service": "multimodal-ai-knowledge-system",
    }


# ==================================================
# ASK
# ==================================================


@app.post(
    "/ask",
    response_model=AskResponse,
    tags=["RAG"],
)
def ask(
    request: AskRequest,
):
    """
    Ask a question to the RAG system.
    """

    logger.info(f"API request received: {request.question}")

    try:

        response = rag_service.ask(request.question)

        logger.success("API request completed successfully.")

        return AskResponse(
            answer=response.answer,
            image_sources=response.image_sources,
            document_sources=response.document_sources,
            web_sources=response.web_sources,
            content_types=response.content_types,
            source_count=response.source_count,
            multimodal=response.multimodal,
            context_relevant=response.context_relevant,
            recovery_attempted=response.recovery_attempted,
            retrieval_attempts=response.retrieval_attempts,
            best_score=response.best_score,
            metadata=response.metadata,
        )

    except Exception as exc:

        logger.exception("RAG API request failed.")

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ==================================================
# UPLOAD
# ==================================================


@app.post(
    "/upload",
    tags=["Ingestion"],
)
async def upload_file(
    file: UploadFile = File(...),
):
    """
    Upload a supported knowledge file
    and index it using the existing
    IndexingService pipeline.
    """

    logger.info(f"Upload request received: {file.filename}")

    # --------------------------------------------------
    # Validate filename
    # --------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    # --------------------------------------------------
    # Supported file types
    # --------------------------------------------------

    allowed_extensions = {
        ".pdf",
        ".txt",
        ".md",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }

    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                f"Supported types: "
                f"{sorted(allowed_extensions)}"
            ),
        )

    # --------------------------------------------------
    # Upload directory
    # --------------------------------------------------

    upload_dir = DATA_ROOT / "uploads"

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------
    # Prevent path traversal
    # --------------------------------------------------

    safe_filename = Path(file.filename).name

    destination = upload_dir / safe_filename

    # --------------------------------------------------
    # Save and index file
    # --------------------------------------------------

    try:

        content = await file.read()

        destination.write_bytes(content)

        logger.info(f"File saved successfully: {destination}")

        # Use the EXISTING indexing pipeline.
        #
        # IndexingService scans the upload directory,
        # loads supported files, chunks them,
        # creates embeddings and stores them in ChromaDB.

        indexing_service.index_directory(str(upload_dir))

        logger.success(f"File indexed successfully: " f"{file.filename}")

        return {
            "status": "success",
            "filename": file.filename,
            "message": ("File uploaded and indexed successfully."),
        }

    except Exception as exc:

        logger.exception("File upload/indexing failed.")

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
