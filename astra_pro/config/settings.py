from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    
    # LLM Configuration (Qwen / 通义千问)
    dashscope_api_key: str = ""
    llm_model: str = "qwen-plus"
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_timeout: int = 30
    
    rate_limit_max_requests: int = 60
    rate_limit_time_window: int = 60
    
    # Embedding Configuration
    embedding_model: str = "text-embedding-v3"

    # RAG / ChromaDB Configuration
    chroma_persist_dir: str = "./chroma_db"
    chunk_size: int = 500
    chunk_overlap: int = 50
    max_file_size_mb: int = 20
    allowed_file_types: list[str] = ["pdf", "docx", "md", "txt"]

    log_level: str = "INFO"


settings = Settings()