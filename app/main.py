from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
from .api import identify

# Import our fish modules
from .models.fish_classifier import FishClassifier
from .models.fish_segmenter import FishSegmenter
from .services.simple_model_manager import SimpleModelManager
from .utils.model_config import get_model_urls, get_cache_dir, get_device

from .state import classifier, segmenter

app = FastAPI(
    title="Fishing-AI API",
    description="API for fish species identification and regulation lookup",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:8080",
        "https://fishai-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model manager instance (using gdown - no credentials needed)
model_manager = SimpleModelManager(get_cache_dir())

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    from . import state 
    try:
        # Get model URLs from configuration (using gdown approach)
        model_urls = get_model_urls()
        
        # Download models from Google Drive using gdown
        logging.info("Downloading models from Google Drive using gdown...")
        success = model_manager.setup_models_from_urls(model_urls)
        
        if not success:
            raise Exception("Failed to download required model files from Google Drive")
        
        # Verify all models are available
        if not model_manager.verify_models():
            raise Exception("Model verification failed")
        
        # Get model paths
        model_paths = model_manager.get_all_model_paths()
        
        # Initialize classifier
        state.classifier = FishClassifier(
            model_path=str(model_paths["classification_model.ts"]),
            data_set_path=str(model_paths["embedding_database.pt"]), 
            indexes_path=str(model_paths["categories.json"]),
            device=get_device()
        )
        
        # Initialize segmenter
        state.segmenter = FishSegmenter(
            model_path=str(model_paths["segmentation_model.ts"]),
            device=get_device()
        )
        
        logging.info("Models loaded successfully from Google Drive using gdown")
        
    except Exception as e:
        logging.error(f"Failed to load models: {e}")
        raise e

# Include routers
app.include_router(identify.router, prefix="/api", tags=["identify"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Fishing-AI API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health")
async def health_check():
    from . import state 
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "models_loaded": {
            "classifier": state.classifier is not None,
            "segmenter": state.segmenter is not None
        },
        "model_info": model_manager.get_model_info(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/models/info")
async def get_model_info():
    """Get detailed information about model files"""
    return model_manager.get_model_info()

@app.post("/models/refresh")
async def refresh_models():
    """Force refresh of model files from Google Drive"""
    try:
        # Clear cache and re-download
        model_manager.clear_cache()
        
        # Re-run startup process
        await startup_event()
        
        return {"message": "Models refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh models: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)