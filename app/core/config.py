import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Creator Assistant API"
    YOUTUBE_API_KEY: str
    GEMINI_API_KEY: str
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()