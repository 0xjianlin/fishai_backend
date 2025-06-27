from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple, Any
import os
from PIL import Image
import io
import numpy as np
import tensorflow as tf
import json
from pathlib import Path
from ..utils.config import settings
from .species_service import species_service
from .regulations_service import regulations_service
from .image_processor import image_processor
from .image_processor import preprocess_for_model

class IdentificationResult(BaseModel):
    species_id: str
    confidence: float
    bounding_box: Optional[Dict[str, float]] = None
    attributes: Optional[Dict[str, Any]] = None

class IdentificationService:
    def __init__(self):
        self.model = None
        self.min_confidence = settings.CONFIDENCE_THRESHOLD
        self.class_mapping = {}
        self.reverse_class_mapping = {}
        self._load_model()
        self._load_class_mapping()

    def _load_class_mapping(self):
        """Load class mapping from file"""
        try:
            mapping_file = Path(settings.MODEL_PATH).parent / "class_mapping.json"
            if mapping_file.exists():
                with open(mapping_file, 'r') as f:
                    mapping_data = json.load(f)
                    self.class_mapping = mapping_data['class_mapping']
                    self.reverse_class_mapping = mapping_data['reverse_mapping']
                print(f"Loaded class mapping for {len(self.class_mapping)} species")
            else:
                print("Class mapping file not found")
        except Exception as e:
            print(f"Error loading class mapping: {e}")

    def _load_model(self):
        """Load the local fish identification model"""
        try:
            model_path = Path(settings.MODEL_PATH)
            if model_path.exists():
                self.model = tf.keras.models.load_model(str(model_path))
                print(f"Loaded model from {model_path}")
            else:
                print(f"Model not found at {model_path}. Please train the model first.")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    async def identify_fish(self, image_data: bytes) -> List[IdentificationResult]:
        """Identify fish in an image using local model"""
        if not self.model:
            raise ValueError("Fish identification model not loaded")
        if not self.class_mapping:
            raise ValueError("Class mapping not loaded")

        try:
            # Preprocess the image
            processed_image = preprocess_for_model(image_data)
            
            # Make prediction
            predictions = self.model.predict(processed_image, verbose=0)
            
            # Process predictions
            results = []
            for pred in predictions[0]:
                confidence = float(pred)
                if confidence >= self.min_confidence:
                    # Get species ID from class mapping
                    class_idx = int(np.argmax(pred))
                    species_id = self.reverse_class_mapping.get(str(class_idx))
                    
                    if species_id:
                        species_info = species_service.get_species(species_id)
                        if species_info:
                            # Get regulations for this species
                            regulations = regulations_service.get_regulations(species_id)
                            
                            results.append(IdentificationResult(
                                species_id=species_id,
                                confidence=confidence,
                                attributes={
                                    "species_info": species_info.dict(),
                                    "regulations": [reg.dict() for reg in regulations]
                                }
                            ))

            return results

        except Exception as e:
            print(f"Error in fish identification: {e}")
            return []

    async def identify_batch(self, images: List[bytes]) -> List[List[IdentificationResult]]:
        """Identify fish in multiple images"""
        results = []
        for image_data in images:
            result = await self.identify_fish(image_data)
            results.append(result)
        return results

    def train_model(self, training_data_dir: str):
        """
        Train the fish identification model using local images
        Args:
            training_data_dir: Path to directory containing training images
        """
        try:
            # TODO: Implement model training using the California fish images
            # This will be implemented in a separate PR
            pass
        except Exception as e:
            print(f"Error training model: {e}")
            raise

# Create a singleton instance
identification_service = IdentificationService() 