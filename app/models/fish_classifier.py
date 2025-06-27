import torch
import numpy as np
import json
import logging
import time
from PIL import Image
from torchvision import transforms
import torch.nn as nn
from typing import List, Dict, Any

class FishClassifier:
    """
    Simplified fish classifier for FastAPI integration
    """
    
    def __init__(self, model_path, data_set_path, indexes_path, device='cpu', threshold=6.84):
        start_time = time.time()
        self.device = device
        self.threshold = threshold
        
        # Load model
        self.model = torch.jit.load(model_path, map_location=device)
        self.model.eval()
        
        # Load database and categories
        self.data_base = torch.load(data_set_path, map_location=device)
        with open(indexes_path, 'r') as f:
            self.indexes = json.load(f)
        
        # Setup transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        self.softmax = nn.Softmax(dim=1)
        elapsed = time.time() - start_time
        logging.info(f"Fish classifier loaded successfully in {elapsed:.2f} seconds")
    
    def classify(self, image_np, top_k=10):
        """
        Classify fish species from numpy image
        
        Args:
            image_np: numpy array of image (H, W, C)
            top_k: number of top predictions to return
            
        Returns:
            list of dictionaries with species info
        """
        # Convert to PIL and transform
        image_pil = Image.fromarray(image_np)
        image_tensor = self.transform(image_pil).unsqueeze(0).to(self.device)
        
        # Get embeddings and FC output
        with torch.no_grad():
            embeddings, fc_output = self.model(image_tensor)
        
        # Get FC classification
        fc_probs = self.softmax(fc_output)
        fc_class_id = torch.argmax(fc_probs, dim=1).item()
        fc_confidence = fc_probs[0][fc_class_id].item()
        
        # Get embedding-based classification
        embedding_results = self._classify_by_embedding(embeddings[0], top_k)
        
        # Combine results
        results = []
        
        # Add FC result
        fc_species = self.indexes['categories'][str(fc_class_id)]
        results.append({
            'common_name': fc_species['name'],
            'scientific_name': fc_species['species_id'],
            'confidence': fc_confidence,
            'method': 'fc_layer'
        })
        
        # Add embedding results
        for result in embedding_results:
            results.append({
                'common_name': result['name'],
                'scientific_name': result['species_id'],
                'confidence': result['accuracy'],
                'method': 'embedding'
            })
        
        # Filter to unique (common_name, scientific_name) pairs, keeping highest confidence
        unique = {}
        for r in results:
            key = (r['common_name'], r['scientific_name'])
            if key not in unique or r['confidence'] > unique[key]['confidence']:
                unique[key] = r
        results = list(unique.values())
        
        # Sort by confidence, descending
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Pad with 'Unknown' if needed
        while len(results) < top_k:
            results.append({
                'common_name': 'Unknown',
                'scientific_name': 'unknown',
                'confidence': 0.0,
                'method': 'none'
            })
        
        return results[:top_k]
    
    def _classify_by_embedding(self, embedding: torch.Tensor, top_k: int = 5) -> List[Dict[str, Any]]:
        """Classify using embedding similarity"""
        # Extract embedding tensor from tuple
        embedding_db = self.data_base[0] if isinstance(self.data_base, tuple) else self.data_base
        # Calculate distances
        distances = (embedding_db - embedding).pow(2).sum(dim=1).sqrt()
        values, indices = torch.sort(distances)

        results = []
        for i in range(min(top_k, len(indices))):
            idx = indices[i]
            # If using tuple, get list_of_ids from self.data_base[1], else from self.indexes
            if isinstance(self.data_base, tuple):
                id_entry = self.data_base[1][idx]
                if isinstance(id_entry, (tuple, list)) and len(id_entry) == 4:
                    internal_id, image_id, annotation_id, drawn_fish_id = id_entry
                else:
                    internal_id = id_entry
                    image_id = annotation_id = drawn_fish_id = None
            else:
                internal_id, image_id, annotation_id, drawn_fish_id = self.indexes['list_of_ids'][idx]
            # Calculate confidence from distance
            confidence = self._distance_to_confidence(distances[idx].item())
            results.append({
                'name': self.indexes['categories'][str(internal_id)]['name'],
                'species_id': self.indexes['categories'][str(internal_id)]['species_id'],
                'accuracy': confidence,
                'distance': distances[idx].item()
            })
        return results
    
    def _distance_to_confidence(self, distance):
        """Convert distance to confidence score"""
        min_dist = 3.5
        max_dist = self.threshold
        delta = max_dist - min_dist
        return max(0.01, 1.0 - (max(min(max_dist, distance), min_dist) - min_dist) / delta) 