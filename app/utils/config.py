import os
from typing import Optional

# Get the absolute path to the backend/app directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings:
    """Simplified settings without .env dependency"""
    
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Fishing-AI API"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Model Settings (now handled by Google Drive)
    DEVICE: str = "cpu"  # "cpu" or "cuda"
    
    # Confidence threshold for predictions
    CONFIDENCE_THRESHOLD: float = 0.2
    
    # Batch processing settings
    MAX_BATCH_SIZE: int = 10
    
    # Image processing settings
    MAX_IMAGE_SIZE: int = 1024  # Maximum image size for processing
    
    # Cloudinary Settings (optional - can be empty)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"

# Create settings instance
settings = Settings() 