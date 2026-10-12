import os
from pydantic import BaseModel

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

        OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
except ImportError:
    class Settings(BaseModel):
        OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

settings = Settings()

MODEL_CONFIG = {
    "qwen3:1.7b": {
        "name": "Qwen3 1.7B",
        "ollama_name": "qwen3:1.7b"
    },
    "qwen3:4b": {
        "name": "Qwen3 4B",
        "ollama_name": "qwen3:4b"
    },
    "qwen2.5-coder:1.5b": {
        "name": "Qwen2.5-Coder 1.5B",
        "ollama_name": "qwen2.5-coder:1.5b"
    }
}
