from urllib.parse import urlparse
import json
import os
import requests

API_KEY = 'AIzaSyAkxdCTBZlqF2gUT3kUjP-cVWmHSYMEnOg'
CX = '830ec732208204808'
OUTPUT_DIR = "D:/fish_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_file_extension(url):
    path = urlparse(url).path  # Get path from URL
    _, ext = os.path.splitext(path)  # Split the path to get extension
    return ext

def google_search(query, api_key, cse_id, num=1):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": cse_id,
        "key": api_key,
        "searchType": "image",
        "num": num,
        "imgType": "photo",
        "rights": "cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial"
    }
    response = requests.get(url, params=params)
    return response.json()

# Load categories.json
with open('D:/Fishing-AI/fishai_backend/models/classification/categories.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)["categories"]

for idx, info in categories.items():
    species_name = info["name"]
    query = species_name + " fish"
    print(f"Searching for: {query}")

    results = google_search(query, API_KEY, CX)
    if "items" in results and len(results["items"]) > 0:
        image_url = results["items"][0]["link"]
        print(f"Downloading: {image_url}")

        ext = get_file_extension(image_url)
        filename = f"{species_name}{ext}"

        response = requests.get(image_url)
        if response.status_code == 200:
            with open(os.path.join(OUTPUT_DIR, filename), "wb") as img_file:
                img_file.write(response.content)
            print("Image downloaded successfully.")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
    else:
        print(f"No image found for {species_name}")