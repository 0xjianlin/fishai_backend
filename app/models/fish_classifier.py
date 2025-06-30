import math
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

    def __init__(self, model_path, data_set_path, indexes_path, device='cpu', threshold=5.0):
        start_time = time.time()
        self.device = device
        self.threshold = threshold

        self.model = torch.jit.load(model_path, map_location=device)
        self.model.eval()

        self.data_base = torch.load(data_set_path, map_location=device)
        with open(indexes_path, 'r') as f:
            self.indexes = json.load(f)

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        self.softmax = nn.Softmax(dim=1)
        elapsed = time.time() - start_time
        logging.info(f"Fish classifier loaded successfully in {elapsed:.2f} seconds")

    def classify(self, image_np, top_k=3):
        image_pil = Image.fromarray(image_np)
        image_tensor = self.transform(image_pil).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(image_tensor)

        if isinstance(outputs, tuple):
            _, fc_output = outputs
        else:
            raise ValueError("Expected model to return a tuple (embedding, fc_output)")

        probs = self.softmax(fc_output).squeeze()
        topk_vals, topk_indices = torch.topk(probs, top_k)

        results = []
        for conf, class_id in zip(topk_vals.tolist(), topk_indices.tolist()):
            species = self.indexes['categories'].get(str(class_id), {
                'name': 'Unknown',
                'species_id': 'unknown'
            })
            results.append({
                'common_name': species['name'],
                'scientific_name': species['species_id'],
                'confidence': conf,
                'method': 'fc_layer'
            })

        logging.debug("classify() [fc_layer only]:")
        for r in results:
            logging.debug(f"  → {r['common_name']} ({r['confidence']:.4f})")

        return results


    def _classify_by_embedding(self, embedding: torch.Tensor, top_k: int = 3) -> List[Dict[str, Any]]:
        if isinstance(self.data_base, tuple):
            db_tensor = self.data_base[0]
            db_ids = self.data_base[1]
        else:
            db_tensor = self.data_base
            db_ids = self.indexes['list_of_ids']

        distances = (db_tensor - embedding).pow(2).sum(dim=1).sqrt()
        values, indices = torch.sort(distances)

        results = []
        for idx in indices[:top_k]:
            idx = idx.item()
            id_entry = db_ids[idx]
            internal_id = id_entry if isinstance(id_entry, int) else id_entry[0]
            distance_val = distances[idx].item()

            category = self.indexes['categories'].get(str(internal_id), {'name': 'Unknown', 'species_id': 'unknown'})
            confidence = self._distance_to_confidence(distance_val)

            print(f"[DEBUG] Distance to {category['name']} ({category['species_id']}): {distance_val:.4f}, confidence={confidence:.4f}")

            results.append({
                'name': category['name'],
                'species_id': category['species_id'],
                'accuracy': confidence,
                'distance': distance_val
            })

        return results

    def _distance_to_confidence(self, distance: float) -> float:
        # Empirically tuned to handle distances 3.5 (close) to 11.5 (far)
        midpoint = 7.0      # Shift the midpoint (closer means more generous)
        steepness = 1.5     # Controls curve slope
        confidence = 1 / (1 + math.exp(steepness * (distance - midpoint)))
        return float(confidence)