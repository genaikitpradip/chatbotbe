

from typing import List
from pydantic_settings import BaseSettings
import os
import json

class Settings(BaseSettings):
    # Azure OpenAI
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment_name: str = "gpt-4o"
    azure_openai_embedding_deployment_name: str = "text-embedding-3-small"
    
    bing_api_key: str
    google_api_key: str
    google_search_engine_id: str
    azure_tts_openai_api_key: str
    azure_tts_openai_api_endpoint: str
    azure_tts_openai_api_version: str = "2024-05-01-preview"
    azure_tts_openai_api_deployment_name: str = "tts-hd"

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "chatgpt_clone"

    # FastAPI
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    upload_dir: str = "uploads"
    max_file_size: int = 10485760  # 10MB

    class Config:
        env_file = ".env"

        @staticmethod
        def parse_env_var(field_name: str, raw_value: str):
            if field_name == "cors_origins":
                try:
                    return json.loads(raw_value)
                except json.JSONDecodeError:
                    return [v.strip() for v in raw_value.split(",")]
            return raw_value

settings = Settings()
os.makedirs(settings.upload_dir, exist_ok=True)
