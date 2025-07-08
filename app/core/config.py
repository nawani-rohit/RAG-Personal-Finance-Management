from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Financial Management System"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_DB: str = "finance_database"
    DATABASE_URL: Optional[str] = None

    # OpenAI settings
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_COMPLETION_MODEL: str = "gpt-4-turbo-preview"
    
    # File processing settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = [".txt", ".pdf", ".doc", ".docx"]
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_CHUNKS_PER_DOCUMENT: int = 20
    
    # Security settings
    CORS_ORIGINS: list = ["*"]  # In production, specify actual domains
    API_KEY_HEADER: str = "X-API-Key"
    
    # Performance settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1
    SIMILARITY_THRESHOLD: float = 0.01
    
    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()