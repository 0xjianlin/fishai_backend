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

# def google_search(query, api_key, cse_id, num=1):
#     url = "https://www.googleapis.com/customsearch/v1"
#     params = {
#         "q": query,
#         "cx": cse_id,
#         "key": api_key,
#         "searchType": "image",
#         "num": num,
#         "imgType": "photo",
#         "rights": "cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial"
#     }
#     response = requests.get(url, params=params)
#     return response.json()

# Load categories.json
with open('D:/Fishing-AI/fishai_backend/models/classification/categories.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)["categories"]

updated_categories = {}

for idx, info in categories.items():
    if info.get('name', '') == info.get('species_id', ''):
        print(info.get('name', ''))

# with open('D:/Fishing-AI/fishai_backend/models/classification/categories_california.json', 'w', encoding='utf-8') as f:
#     json.dump(updated_categories, f, ensure_ascii=False, indent=4)

print("Done")