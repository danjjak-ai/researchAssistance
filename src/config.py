from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # LLM
    GOOGLE_API_KEY: str
    GEMINI_MODEL_PRIMARY: str = "gemini-2.5-flash"
    GEMINI_MODEL_FAST: str = "gemini-2.5-flash"

    # APIs
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None

    # Database & Persistence
    POSTGRES_URL: str = "postgresql://user:pass@localhost:5432/research_assistant"
    CHROMA_PERSIST_DIR: str = "./data/chroma"

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    VAULT_DIR: Path = Path("vault")
    RAW_DIR: Path = Path("vault/raw")
    WIKI_DIR: Path = Path("vault/wiki")

    # Parsing
    PDF_PARSER_PRIMARY: str = "mineru"
    PDF_PARSER_FALLBACK: str = "marker"
    USE_GPU: bool = True

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 7860
    MAX_ITERATIONS: int = 3
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
