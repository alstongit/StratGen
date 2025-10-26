from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    JWT_SECRET: str
    
    # AI
    GOOGLE_API_KEY: str  # Gemini API key
    
    # External Services
    SERPER_API_KEY: str  # Serper.dev API key
    
    # App
    FRONTEND_URL: str = "http://localhost:5173"
    ENVIRONMENT: str = "development"
    
    # Instagram automation
    INSTAGRAM_USERNAME: str
    INSTAGRAM_PASSWORD: str
    INSTAGRAM_HEADLESS: bool = Field(default=False)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()