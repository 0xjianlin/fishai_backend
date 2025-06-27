#!/usr/bin/env python3
"""
Test script for the new FastAPI endpoints
"""
import requests
import json
from PIL import Image
import numpy as np
import io

# API base URL
BASE_URL = "http://localhost:8088/api"

def create_test_image():
    """Create a simple test image"""
    # Create a 224x224 RGB image with some color
    img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_species_list():
    """Test species list endpoint"""
    print("Testing species list endpoint...")
    response = requests.get(f"{BASE_URL}/species-list")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total species: {data.get('total_species', 0)}")
    if data.get('species'):
        print(f"First few species: {data['species'][:3]}")
    print()

def test_classify_only():
    """Test classify-only endpoint"""
    print("Testing classify-only endpoint...")
    
    # Create test image
    img_bytes = create_test_image()
    
    # Send request
    files = {'file': ('test.png', img_bytes, 'image/png')}
    response = requests.post(f"{BASE_URL}/classify-only", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        if data.get('classifications'):
            print(f"Classifications: {data['classifications'][:2]}")
    else:
        print(f"Error: {response.text}")
    print()

def test_detect_and_classify():
    """Test detect-and-classify endpoint"""
    print("Testing detect-and-classify endpoint...")
    
    # Create test image
    img_bytes = create_test_image()
    
    # Send request
    files = {'file': ('test.png', img_bytes, 'image/png')}
    response = requests.post(f"{BASE_URL}/detect-and-classify", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Total fish detected: {data.get('total_fish_detected', 0)}")
        if data.get('detections'):
            print(f"First detection: {data['detections'][0]}")
    else:
        print(f"Error: {response.text}")
    print()

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get("http://localhost:8088/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

if __name__ == "__main__":
    print("Testing new FastAPI endpoints...")
    print("=" * 50)
    
    try:
        test_root()
        test_health()
        test_species_list()
        test_classify_only()
        test_detect_and_classify()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure it's running on localhost:8088")
    except Exception as e:
        print(f"Error during testing: {e}") 