"""
Centralized application configuration.

Every module imports configuration from this file.
Never hardcode API keys or paths elsewhere.
"""
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load .env before reading variables
load_dotenv()


class Settings(BaseSettings):

    APP_NAME: str = Field(default="Multimodal AI Knowledge System")
    LOG_LEVEL: str = Field(default="INFO")

    OPENAI_API_KEY: str = Field(default="")
    GEMINI_API_KEY: str = Field(default="")
    ANTHROPIC_API_KEY: str = Field(default="")

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    CHROMA_DB_PATH: str = "storage/chroma_db"
    CHROMA_COLLECTION_NAME: str = "knowledge_base"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data Directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CHROMA_DIR = PROJECT_ROOT / settings.CHROMA_DB_PATH

# Log Directory
LOG_DIR = PROJECT_ROOT / "logs"

# Create directories automatically
for directory in [
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    CHROMA_DIR,
    LOG_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)