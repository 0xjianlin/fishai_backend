from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from ..utils.config import settings
import os
import logging
import cv2
import numpy as np
import io
from PIL import Image
from ..utils.util import extract_fish_region
from .. import state
import json
from pathlib import Path
import time

BASE_DIR = Path(__file__).parent.parent.parent.resolve()

router = APIRouter()

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))

reg_path = BASE_DIR / "references" / "regulation" / "regulations.json"
with open(reg_path, 'r', encoding='utf-8') as f:
    REGULATIONS = json.load(f)["regulations"]

categories_path = BASE_DIR / "models" / "classification" / "categories_california.json"
with open(categories_path, 'r', encoding='utf-8') as f:
    CATEGORIES = json.load(f)

def find_regulation(common_name, scientific_name):
    try:
        for reg in REGULATIONS:
            if reg.get('species', '').lower() == common_name.lower() or reg.get('latin_name', '').lower() == scientific_name.lower():
                return reg
        return {}        
    except Exception as e:
        logging.error(f"Error in find_regulation: {e}")
        return {}

def find_category(common_name, scientific_name):
    try:
        for cat in CATEGORIES['categories'].values():
            if cat.get('name', '').lower() == common_name.lower() or cat.get('species_id', '').lower() == scientific_name.lower():
                return cat
        return ""
    except Exception as e:
        logging.error(f"Error in find_regulation: {e}")
        return ""

@router.post("/identify")
async def detect_and_classify_batch(files: List[UploadFile] = File(...)):
    if state.classifier is None or state.segmenter is None:
        raise HTTPException(status_code=503, detail="AI models not loaded")

    batch_results = []
    for file in files:
        file_start = time.time()
        if not file.content_type.startswith('image/'):
            batch_results.append({"error": "File must be an image", "filename": file.filename})
            continue

        try:
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            image_np = np.array(image)

            print(f"[DEBUG] Processing {file.filename}, shape={image_np.shape}")

            if len(image_np.shape) != 3:
                batch_results.append({"error": "Image must be RGB", "filename": file.filename})
                continue

            polygons, masks = state.segmenter.segment(image_np)
            print(f"[DEBUG] Segmented {len(polygons)} fish in {file.filename}")

            results = []
            for i, (polygon, mask) in enumerate(zip(polygons, masks)):
                try:
                    fish_region = extract_fish_region(image_np, mask)
                    print(f"[DEBUG] Fish region shape: {fish_region.shape}")
                    if fish_region.shape[0] < 50 or fish_region.shape[1] < 50:
                        print(f"[DEBUG] Skipping small fish region in {file.filename}")
                        continue

                    classifications = state.classifier.classify(fish_region, top_k=10)

                    if not classifications or all(c['common_name'] == "Unknown" for c in classifications):
                        print(f"[DEBUG] No valid classification for fish {i} in {file.filename}")

                    print(f"[DEBUG] Classifications for fish {i} in {file.filename}:")
                    for c in classifications:
                        print(f"  → {c['common_name']} ({c['confidence']:.4f}) via {c['method']}")

                    points = [(polygon[f"x{j+1}"], polygon[f"y{j+1}"]) for j in range(len(polygon)//2)]
                    points = np.array(points)
                    x1, y1 = points.min(axis=0)
                    x2, y2 = points.max(axis=0)

                    results.append({
                        "fish_id": i,
                        "bounding_box": {
                            "x1": int(x1), "y1": int(y1),
                            "x2": int(x2), "y2": int(y2)
                        },
                        "polygon": polygon,
                        "classifications": classifications,
                        "mask_area": int(cv2.countNonZero(mask))
                    })
                except Exception as e:
                    logging.error(f"Error processing fish {i}: {e}")
                    continue

            batch_results.append({
                "filename": file.filename,
                "success": True,
                "total_fish_detected": len(results),
                "detections": results
            })

        except Exception as e:
            batch_results.append({"error": str(e), "filename": file.filename})

    ret_results = []
    for result in batch_results:
        if 'success' not in result:
            continue
        unique_common_names = []
        result_line = {
            "filename": result['filename'],
            "success": result['success'],
            "total_fish_detected": result['total_fish_detected'],
            "detections": []
        }
        for detection in result['detections']:
            for classification in detection['classifications']:
                if classification['common_name'] not in unique_common_names and classification['common_name'] != "Unknown":
                    unique_common_names.append(classification['common_name'])
                    regulation = find_regulation(classification['common_name'], classification['scientific_name'])
                    category = find_category(classification['common_name'], classification['scientific_name'])
                    result_line['detections'].append({
                        "common_name": classification['common_name'],
                        "scientific_name": classification['scientific_name'],
                        "confidence": classification['confidence'],
                        "image_url": category.get('image_url', ''),
                        "more_info": regulation
                    })
        if not result_line['detections']:
            print(f"[INFO] No confident classifications found for {result['filename']}")
        ret_results.append(result_line)

    return {"success": True, "results": ret_results}

@router.get("/species")
async def get_species_list():
    """Get list of all supported fish species"""
    try:
        if state.classifier is None:
            raise HTTPException(status_code=503, detail="Classifier not loaded")
        
        species_list = []
        for cat_id, cat_info in state.classifier.indexes['categories'].items():
            regulation = find_regulation(cat_info['name'], cat_info['species_id'])
            image_url = cat_info.get('image_url', '')
            species_list.append({
                "id": cat_id,
                "name": cat_info['name'],
                "species_id": cat_info['species_id'],
                "image_url": image_url,
                "more_info": regulation,
                "location": cat_info.get('location', '')
            })
        
        return {
            "success": True,
            "total_species": len(species_list),
            "species": species_list
        }
        
    except Exception as e:
        logging.error(f"Error getting species list: {e}")
        raise HTTPException(status_code=500, detail=str(e))