from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"  # Ignore extra fields from .env file
    )
    
    # Database
    database_url: str = "postgresql://postgres:dali2004@localhost:5432/universety_db"
    
    # App Info
    app_name: str = "University Management API"
    app_description: str = "Complete university management system with PostgreSQL and Prisma"
    app_version: str = "2.0.0"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    cors_origins: list = ["*"]  # In production, replace with specific domains
    
    # Email Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "Plateforme Universitaire"


settings = Settings()