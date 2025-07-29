import os
from typing import List, Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API Configuration
    api_title: str = "Presidio Anonymization Backend"
    api_version: str = "1.0.0"
    api_description: str = "Advanced anonymization backend with FastAPI and Presidio"
    
    # Development settings
    debug: bool = False
    reload: bool = False
    
    # CORS settings
    allowed_origins: List[str] = ["http://localhost:8080", "http://localhost:3000"]
    
    # Presidio services
    presidio_analyzer_api_url: str = "http://localhost:5002"
    presidio_analyzer_api_key: Optional[str] = None
    presidio_anonymizer_api_url: str = "http://localhost:5001"
    presidio_anonymizer_api_key: Optional[str] = None
    
    # Backend mode: 'local' or 'external'
    anonymization_mode: str = "local"
    
    # File handling
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "./uploads"
    results_dir: str = "./results"
    
    # OCR settings
    tesseract_cmd: str = "/usr/bin/tesseract"
    ocr_language: str = "eng"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
        # Convert comma-separated values to lists
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name == 'allowed_origins':
                return [origin.strip() for origin in raw_val.split(',')]
            return cls.json_loads(raw_val)


# Create settings instance
settings = Settings()
