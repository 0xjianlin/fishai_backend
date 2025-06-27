import numpy as np
from typing import List, Dict, Optional
import os
import logging
from PIL import Image
import io
from .fish_classifier import FishClassifier
from .fish_segmenter import FishSegmenter
from ..utils.config import settings

class FishPredictor:
    def __init__(self, model_path: str = None):
        """
        Initialize the advanced fish species predictor
        Supports segmentation and classification (PyTorch only)
        """
        self.classifier = None
        self.segmenter = None
        self.model_path = model_path or settings.MODEL_PATH
        self._load_advanced_models()
        if not self.classifier:
            raise RuntimeError("No advanced classification model found. Please check your model files.")

    def _load_advanced_models(self):
        """Load the advanced fish identification models (PyTorch only)"""
        try:
            classification_model_path = os.path.join(settings.MODELS_DIR, "classification_model.ts")
            segmentation_model_path = os.path.join(settings.MODELS_DIR, "segmentation_model.ts")
            embedding_db_path = os.path.join(settings.MODELS_DIR, "embedding_database.pt")
            categories_path = os.path.join(settings.MODELS_DIR, "categories.json")

            # Use absolute paths for robustness
            classification_model_path = os.path.abspath(classification_model_path)
            segmentation_model_path = os.path.abspath(segmentation_model_path)
            embedding_db_path = os.path.abspath(embedding_db_path)
            categories_path = os.path.abspath(categories_path)

            # Check for required files
            if all(os.path.exists(path) for path in [classification_model_path, embedding_db_path, categories_path]):
                self.classifier = FishClassifier(
                    model_path=classification_model_path,
                    data_set_path=embedding_db_path,
                    indexes_path=categories_path,
                    device=settings.DEVICE
                )
                logging.info("Advanced fish classifier loaded successfully")
            else:
                missing = [path for path in [classification_model_path, embedding_db_path, categories_path] if not os.path.exists(path)]
                logging.error(f"Missing model files: {missing}")
                self.classifier = None

            if os.path.exists(segmentation_model_path):
                self.segmenter = FishSegmenter(
                    model_path=segmentation_model_path,
                    device=settings.DEVICE
                )
                logging.info("Fish segmenter loaded successfully")
            else:
                self.segmenter = None
        except Exception as e:
            logging.warning(f"Failed to load advanced models: {e}")
            self.classifier = None
            self.segmenter = None

    def predict(self, image_data: bytes) -> List[Dict]:
        """
        Predict fish species from image using advanced models only
        Returns list of predictions with confidence scores
        """
        if not self.classifier:
            raise RuntimeError("No advanced classification model found. Please check your model files.")
        try:
            image = Image.open(io.BytesIO(image_data))
            image_np = np.array(image)
            return self._predict_advanced(image_np)
        except Exception as e:
            raise RuntimeError(f"Error making prediction: {str(e)}")

    def _predict_advanced(self, image_np: np.ndarray) -> List[Dict]:
        # Always use classification only, skip segmentation
        return self._predict_classification_only(image_np)

    def _predict_with_segmentation(self, image_np: np.ndarray) -> List[Dict]:
        # Segmentation is disabled
        return self._predict_classification_only(image_np)

    def _predict_classification_only(self, image_np: np.ndarray) -> List[Dict]:
        try:
            classifications = self.classifier.classify(image_np, top_k=5)
            results = []
            for classification in classifications:
                results.append({
                    'species_id': classification['species_id'],
                    'name': classification['name'],
                    'confidence': classification['confidence'],
                    'method': classification['method']
                })
            return results
        except Exception as e:
            logging.error(f"Classification prediction failed: {e}")
            return []

    def predict_batch(self, image_data_list: List[bytes]) -> List[List[Dict]]:
        """
        Predict fish species from multiple images using advanced models only
        """
        if not self.classifier:
            raise RuntimeError("No advanced classification model found. Please check your model files.")
        try:
            results = []
            for image_data in image_data_list:
                image_results = self.predict(image_data)
                results.append(image_results)
            return results
        except Exception as e:
            raise RuntimeError(f"Error making batch predictions: {str(e)}")

    def get_species_list(self) -> List[Dict[str, str]]:
        if self.classifier:
            return self.classifier.get_species_list()
        else:
            return []

    def get_species_info(self, species_id: str) -> Optional[Dict]:
        if self.classifier:
            return self.classifier.get_species_info(species_id)
        else:
            return None 