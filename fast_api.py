from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from PIL import Image
import io
import logging
import os
from typing import List, Dict, Any

# Import our fish modules
from app.models.fish_classifier import FishClassifier
from app.models.fish_segmenter import FishSegmenter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fish Identification API",
    description="API for fish detection, segmentation, and species classification",
    version="1.0.0"
)

# CORS middleware for Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Vue dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances
classifier = None
segmenter = None

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global classifier, segmenter
    
    try:
        # Initialize classifier
        classifier = FishClassifier(
            model_path="models/classification/classification_model.ts",
            data_set_path="models/classification/embedding_database.pt", 
            indexes_path="models/classification/categories.json",
            device="cpu"  # Change to "cuda" if GPU available
        )
        
        # Initialize segmenter
        segmenter = FishSegmenter(
            model_path="models/classification/segmentation_model.ts",
            device="cpu"  # Change to "cuda" if GPU available
        )
        
        logger.info("Models loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise e

def extract_fish_region(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Extract fish region using segmentation mask"""
    # Ensure mask is uint8 and same size as image
    if mask.dtype != np.uint8:
        mask = mask.astype(np.uint8)
    if mask.shape[:2] != image.shape[:2]:
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
    # Apply mask to image
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    
    # Find bounding box of mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image  # Return full image if no contours found
    
    # Get largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Extract region with some padding
    padding = 10
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(image.shape[1], x + w + padding)
    y2 = min(image.shape[0], y + h + padding)
    
    return image[y1:y2, x1:x2]

@app.post("/api/classify-only")
async def classify_fish_only(file: UploadFile = File(...)):
    """
    Classify fish species from entire image (no segmentation)
    
    Useful when you know the image contains a single fish
    """
    try:
        # Read and validate image
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)
        
        # Classify entire image
        classifications = classifier.classify(image_np, top_k=5)
        
        return {
            "success": True,
            "classifications": classifications
        }
        
    except Exception as e:
        logger.error(f"Error in classify_only: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/segment-only")
async def segment_fish_only(file: UploadFile = File(...)):
    """
    Only segment fish from image (no classification)
    
    Returns fish masks and polygons
    """
    try:
        # Read and validate image
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)
        
        # Segment fish
        polygons, masks = segmenter.segment(image_np)
        
        # Convert masks to base64 for frontend display
        mask_data = []
        for i, mask in enumerate(masks):
            # Convert mask to image format
            mask_img = Image.fromarray(mask)
            buffer = io.BytesIO()
            mask_img.save(buffer, format='PNG')
            mask_base64 = buffer.getvalue()
            
            mask_data.append({
                "fish_id": i,
                "mask": mask_base64,
                "polygon": polygons[i]
            })
        
        return {
            "success": True,
            "total_fish_detected": len(masks),
            "segments": mask_data
        }
        
    except Exception as e:
        logger.error(f"Error in segment_only: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": classifier is not None and segmenter is not None
    }

@app.get("/api/species-list")
async def get_species_list():
    """Get list of all supported fish species"""
    try:
        if classifier is None:
            raise HTTPException(status_code=503, detail="Classifier not loaded")
        
        species_list = []
        for cat_id, cat_info in classifier.indexes['categories'].items():
            species_list.append({
                "id": cat_id,
                "name": cat_info['name'],
                "species_id": cat_info['species_id']
            })
        
        return {
            "success": True,
            "total_species": len(species_list),
            "species": species_list
        }
        
    except Exception as e:
        logger.error(f"Error getting species list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 