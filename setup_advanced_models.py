#!/usr/bin/env python3
"""
Setup script for advanced fish identification models
Downloads and configures the latest models for the fishingmvp1 project
"""

import os
import sys
import requests
import zipfile
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Model URLs
MODEL_URLS = {
    "classification": "https://storage.googleapis.com/fishial-ml-resources/classification_rectangle_v7-1.zip",
    "segmentation": "https://storage.googleapis.com/fishial-ml-resources/segmentator_fpn_res18_416_1.zip",
    "detection": "https://storage.googleapis.com/fishial-ml-resources/detector_v10_m3.zip"
}

def create_directories():
    """Create necessary directories"""
    dirs = ["models", "models/classification", "models/segmentation", "models/detection"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")

def download_file(url, filename, chunk_size=8192):
    """Download a file with progress indication"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        logger.info(f"Downloading {filename}...")
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        logger.info(f"Progress: {percent:.1f}%")
        
        logger.info(f"Downloaded {filename} successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download {filename}: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """Extract zip file to directory"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logger.info(f"Extracted {zip_path} to {extract_to}")
        return True
    except Exception as e:
        logger.error(f"Failed to extract {zip_path}: {e}")
        return False

def setup_models():
    """Download and setup all models"""
    create_directories()
    
    for model_type, url in MODEL_URLS.items():
        logger.info(f"\n{'='*50}")
        logger.info(f"Setting up {model_type} model")
        logger.info(f"{'='*50}")
        
        # Download model
        zip_filename = f"models/{model_type}_model.zip"
        if download_file(url, zip_filename):
            # Extract model
            extract_dir = f"models/{model_type}"
            if extract_zip(zip_filename, extract_dir):
                # Clean up zip file
                os.remove(zip_filename)
                logger.info(f"Cleaned up {zip_filename}")
            else:
                logger.error(f"Failed to extract {model_type} model")
        else:
            logger.error(f"Failed to download {model_type} model")

def create_model_config():
    """Create model configuration file"""
    config = {
        "models": {
            "classification": {
                "model_path": "models/classification/classification_model.ts",
                "embedding_db_path": "models/classification/embedding_database.pt",
                "categories_path": "models/classification/categories.json"
            },
            "segmentation": {
                "model_path": "models/segmentation/segmentation_model.ts"
            },
            "detection": {
                "model_path": "models/detection/detection_model.ts"
            }
        },
        "settings": {
            "device": "cpu",
            "confidence_threshold": 0.2,
            "max_batch_size": 10
        }
    }
    
    config_path = "models/model_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Created model configuration: {config_path}")

def check_model_files():
    """Check if all required model files exist"""
    required_files = [
        "models/classification/classification_model.ts",
        "models/classification/embedding_database.pt",
        "models/classification/categories.json",
        "models/segmentation/segmentation_model.ts"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.warning("Missing model files:")
        for file_path in missing_files:
            logger.warning(f"  - {file_path}")
        return False
    else:
        logger.info("All required model files are present!")
        return True

def create_env_file():
    """Create .env file with model paths"""
    env_content = """# Fish Identification API Configuration

# Model Settings
MODELS_DIR=models/classification
DEVICE=cpu
CONFIDENCE_THRESHOLD=0.2
MAX_BATCH_SIZE=10

# API Settings
API_V1_STR=/api
PROJECT_NAME=Fishing-AI API

# CORS Settings
BACKEND_CORS_ORIGINS=["*"]

# Cloudinary Settings (optional)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Security Settings
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
"""
    
    with open(".env", 'w') as f:
        f.write(env_content)
    
    logger.info("Created .env file with default configuration")

def main():
    """Main setup function"""
    logger.info("Starting advanced fish identification model setup...")
    
    try:
        # Setup models
        setup_models()
        
        # Create configuration files
        create_model_config()
        create_env_file()
        
        # Check if everything is set up correctly
        if check_model_files():
            logger.info("\n" + "="*60)
            logger.info("🎉 Setup completed successfully!")
            logger.info("="*60)
            logger.info("Your fishingmvp1 project now has advanced fish identification capabilities:")
            logger.info("✅ 426 fish species classification")
            logger.info("✅ Fish segmentation and detection")
            logger.info("✅ Multiple fish detection in single images")
            logger.info("✅ High-accuracy species identification")
            logger.info("\nNext steps:")
            logger.info("1. Install dependencies: pip install -r backend/requirements.txt")
            logger.info("2. Start the backend: cd backend && python run.py")
            logger.info("3. Start the frontend: cd frontend && npm run serve")
            logger.info("4. Visit http://localhost:8080 to use the application")
        else:
            logger.error("\n❌ Setup incomplete. Some model files are missing.")
            logger.error("Please check the download logs above and try again.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 