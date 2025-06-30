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
            embeddings, fc_output = outputs
        else:
            raise ValueError("Expected model to return a tuple (embedding, fc_output)")

        # FC Prediction
        fc_probs = self.softmax(fc_output)
        fc_class_id = torch.argmax(fc_probs, dim=1).item()
        fc_confidence = fc_probs[0][fc_class_id].item()

        fc_species = self.indexes['categories'].get(str(fc_class_id), {
            'name': 'Unknown',
            'species_id': 'unknown'
        })

        results = [{
            'common_name': fc_species['name'],
            'scientific_name': fc_species['species_id'],
            'confidence': fc_confidence,
            'method': 'fc_layer',
            'raw_fc': fc_confidence,
            'raw_embed': 0.0
        }]

        # Embedding-based top matches (expanded)
        embedding_results = self._classify_by_embedding(embeddings[0], top_k=30)

        for r in embedding_results:
            results.append({
                'common_name': r['name'],
                'scientific_name': r['species_id'],
                'confidence': r['accuracy'],
                'method': 'embedding',
                'raw_fc': 0.0,
                'raw_embed': r['accuracy']
            })

        # Merge duplicates, prefer combined confidence
        combined_scores = {}
        for r in results:
            key = (r['common_name'], r['scientific_name'])
            if key not in combined_scores:
                combined_scores[key] = r
            else:
                # Combine scores if from different sources
                combined_scores[key]['raw_fc'] = max(combined_scores[key]['raw_fc'], r['raw_fc'])
                combined_scores[key]['raw_embed'] = max(combined_scores[key]['raw_embed'], r['raw_embed'])

        # Final reweighting
        blended_results = []
        for r in combined_scores.values():
            # Weighting: adjust as needed (embedding trusted more here)
            combined_conf = 0.4 * r['raw_fc'] + 0.6 * r['raw_embed']
            r['confidence'] = combined_conf
            blended_results.append(r)

        # Sort and truncate
        sorted_results = sorted(blended_results, key=lambda x: x['confidence'], reverse=True)[:top_k]

        logging.debug("classify() results:")
        for r in sorted_results:
            logging.debug(f"  → {r['common_name']} ({r['confidence']:.4f}) via blend: fc={r['raw_fc']:.4f}, embed={r['raw_embed']:.4f}")

        return sorted_results

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
        # return float(1 / (1 + math.exp(1.0 * (distance - 8.0))))  # Slower dropoff, midpoint=8
        return max(0.01, 1.0 - min(distance / 15.0, 0.99))
