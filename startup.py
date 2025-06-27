#!/usr/bin/env python3
"""
Startup script for Railway deployment
Handles model downloads and provides graceful error handling
"""

import os
import sys
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required packages are available"""
    try:
        import fastapi
        import uvicorn
        import cv2
        import torch
        import numpy as np
        import PIL
        logger.info("✅ All core dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def setup_model_cache():
    """Create cache directory for models"""
    try:
        cache_dir = Path("cache/models")
        cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Cache directory created: {cache_dir}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create cache directory: {e}")
        return False

def download_models():
    """Download models from Google Drive"""
    try:
        from app.services.simple_model_manager import SimpleModelManager
        from app.utils.model_config import get_model_urls, get_cache_dir
        
        model_manager = SimpleModelManager(get_cache_dir())
        model_urls = get_model_urls()
        
        logger.info("📥 Downloading models from Google Drive...")
        success = model_manager.setup_models_from_urls(model_urls)
        
        if success:
            logger.info("✅ Models downloaded successfully")
            return True
        else:
            logger.warning("⚠️ Model download failed, but continuing...")
            return False
            
    except Exception as e:
        logger.warning(f"⚠️ Model download error: {e}")
        logger.info("Continuing without models (they will be downloaded on first request)")
        return False

def main():
    """Main startup function"""
    logger.info("🚀 Starting Fishing-AI API setup...")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependency check failed")
        sys.exit(1)
    
    # Setup cache
    if not setup_model_cache():
        logger.error("❌ Cache setup failed")
        sys.exit(1)
    
    # Try to download models (non-blocking)
    download_models()
    
    # Start the application
    logger.info("🎯 Starting FastAPI application...")
    
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main() 