from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    PROJECT_NAME: str = "Prism AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./prism_ai.db"
    
    # Vector database settings
    CHROMADB_PATH: str = "./chroma_db"
    
    # LLM settings
    LLM_PROVIDER: str = "gemini"  # Options: gemini, glm, mistral
    GEMINI_API_KEY: str = ""
    GLM_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    
    # Cloud storage settings
    GOOGLE_DRIVE_CLIENT_ID: str = ""
    GOOGLE_DRIVE_CLIENT_SECRET: str = ""
    
    # Payment processing
    DARAJA_CONSUMER_KEY: str = ""
    DARAJA_CONSUMER_SECRET: str = ""
    DARAJA_SHORTCODE: str = ""
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()