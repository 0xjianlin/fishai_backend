import math
import torch
import numpy as np
import json
import logging
import time
from PIL import Image
from torchvision import transforms
from typing import List, Dict, Any

class FishClassifier:
    """
    Fish classifier using only embedding-based similarity (no FC layer).
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

        elapsed = time.time() - start_time
        logging.info(f"Embedding-based fish classifier loaded in {elapsed:.2f} seconds")

    def classify(self, image_np, top_k=3):
        image_pil = Image.fromarray(image_np)
        image_tensor = self.transform(image_pil).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(image_tensor)

        if not isinstance(outputs, tuple) or len(outputs) != 2:
            raise ValueError("Expected model to return a tuple (embedding, fc_output)")

        embedding = outputs[0][0]  # First item is the embedding

        # Run embedding similarity
        return self._classify_by_embedding(embedding, top_k)

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
        seen_species = set()
        for idx in indices:
            idx = idx.item()
            id_entry = db_ids[idx]
            internal_id = id_entry if isinstance(id_entry, int) else id_entry[0]
            category = self.indexes['categories'].get(str(internal_id), {'name': 'Unknown', 'species_id': 'unknown'})

            # Ensure uniqueness of species
            if category['species_id'] in seen_species:
                continue

            seen_species.add(category['species_id'])
            distance_val = distances[idx].item()
            confidence = self._distance_to_confidence(distance_val)

            results.append({
                'common_name': category['name'],
                'scientific_name': category['species_id'],
                'confidence': confidence,
                'method': 'embedding'
            })

            if len(results) >= top_k:
                break

        return results

    def _distance_to_confidence(self, distance: float) -> float:
        max_distance = 14
        min_distance = 3
        normalized = max(0.0, min(1.0, (max_distance - distance) / (max_distance - min_distance)))
        return round(normalized, 4)