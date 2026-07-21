import os
from pathlib import Path
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMSettings(BaseModel):
    url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    model: str = Field(default="midnight-agent", description="Model name for reasoning and chat")
    embedding_model: str = Field(default="nomic-embed-text", description="Model name for vector embeddings")
    temperature: float = Field(default=0.2, description="Sampling temperature")
    context_length: int = Field(default=8192, description="Context window size")

class ExecutorSettings(BaseModel):
    default_wsl_distro: str = Field(default="kali-linux", description="Default WSL distribution")
    timeout_seconds: int = Field(default=120, description="Command execution timeout in seconds")
    allowed_commands: List[str] = Field(
        default=["nmap", "ping", "whoami", "uname", "ls", "cat", "grep", "curl", "git", "python", "python3"],
        description="Command prefixes allowed without explicit approval (if auto-approve matches)"
    )
    auto_approve_level: str = Field(default="high", description="Auto-approval level: none, low, high")

class StorageSettings(BaseModel):
    base_dir: str = Field(default="C:/midnight_agent/storage", description="Base directory for persistence")
    db_path: str = Field(default="C:/midnight_agent/storage/midnight_core.db", description="SQLite database path")
    rag_dir: str = Field(default="C:/midnight_agent/storage/rag", description="RAG document upload storage")

class DashboardSettings(BaseModel):
    host: str = Field(default="127.0.0.1", description="Dashboard binding host")
    port: int = Field(default=8000, description="Dashboard binding port")
    debug: bool = Field(default=False, description="FastAPI debug mode")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MIDNIGHT_", env_nested_delimiter="__")
    
    llm: LLMSettings = Field(default_factory=LLMSettings)
    executor: ExecutorSettings = Field(default_factory=ExecutorSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    dashboard: DashboardSettings = Field(default_factory=DashboardSettings)
    log_level: str = Field(default="INFO", description="Console & file log level")

    def create_directories(self) -> None:
        """Create necessary storage directories."""
        Path(self.storage.base_dir).mkdir(parents=True, exist_ok=True)
        Path(self.storage.rag_dir).mkdir(parents=True, exist_ok=True)
        Path(os.path.dirname(self.storage.db_path)).mkdir(parents=True, exist_ok=True)

# Global settings instance
settings = Settings()
settings.create_directories()
