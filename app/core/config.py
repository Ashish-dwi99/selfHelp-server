import os
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Khoj AI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./khoj.db")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyDwZzWWjMOtYZrJptTplnoww-kJxcswYyI")
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # File upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: List[str] = ["txt", "pdf", "md", "org", "docx"]
    
    class Config:
        case_sensitive = True


settings = Settings()
