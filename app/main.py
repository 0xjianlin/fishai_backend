from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from PIL import Image
import io
import logging
import os
from typing import List, Dict, Any
from datetime import datetime
from .api import identify

# Import our fish modules
from .models.fish_classifier import FishClassifier
from .models.fish_segmenter import FishSegmenter

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
        "https://californiafishspecies.vercel.app/"  # Update this with your frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    from . import state 
    try:
        # Initialize classifier
        state.classifier = FishClassifier(
            model_path="models/classification/classification_model.ts",
            data_set_path="models/classification/embedding_database.pt", 
            indexes_path="models/classification/categories.json",
            device="cpu"  # Change to "cuda" if GPU available
        )
        
        # Initialize segmenter
        state.segmenter = FishSegmenter(
            model_path="models/classification/segmentation_model.ts",
            device="cpu"  # Change to "cuda" if GPU available
        )
        
        logging.info("Models loaded successfully")
        
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
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)