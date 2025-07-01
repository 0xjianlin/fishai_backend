# from urllib.parse import urlparse
# import json
# import os
# import requests

# API_KEY = 'AIzaSyAkxdCTBZlqF2gUT3kUjP-cVWmHSYMEnOg'
# CX = '830ec732208204808'
# OUTPUT_DIR = "D:/fish_images"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# def get_file_extension(url):
#     path = urlparse(url).path  # Get path from URL
#     _, ext = os.path.splitext(path)  # Split the path to get extension
#     return ext

# # def google_search(query, api_key, cse_id, num=1):
# #     url = "https://www.googleapis.com/customsearch/v1"
# #     params = {
# #         "q": query,
# #         "cx": cse_id,
# #         "key": api_key,
# #         "searchType": "image",
# #         "num": num,
# #         "imgType": "photo",
# #         "rights": "cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial"
# #     }
# #     response = requests.get(url, params=params)
# #     return response.json()

# # Load categories.json
# # with open('D:/Fishing-AI/fishai_backend/models/classification/categories_california.json', 'r', encoding='utf-8') as f:
# #     categories = json.load(f)["categories"]

# # updated_categories = []

# # for root, dirs, files in os.walk("D:/data_for_california_fish"):
# #     for file in files:
# #         directory = os.path.basename(root)
# #         updated_categories.append({
# #             'filename': directory + "/" + file,
# #             'species_id': directory,
# #         })
# #         # for directory in dirs:
# #         #     if directory == info['name']:
# #         #         os.rename(os.path.join(root, directory), os.path.join(root, info['species_id']))

# # with open('D:/Fishing-AI/fishai_backend/models/classification/data_train.json', 'w', encoding='utf-8') as f:
# #     json.dump(updated_categories, f, ensure_ascii=False, indent=4)

# # # print("Done")


import os
import json

# Path to your data folder
data_root = r"D:\data_for_california_fish"  # change this if needed

# Output path for the annotation file
output_json = os.path.join(data_root, "data_train.json")

annotations = []

for species_name in os.listdir(data_root):
    species_dir = os.path.join(data_root, species_name)
    if os.path.isdir(species_dir):
        for img_file in os.listdir(species_dir):
            annotations.append({
                "file_name": f"{species_name}/{img_file}",
                "species_id": species_name
            })

# Save to JSON
with open(output_json, "w") as f:
    json.dump(annotations, f, indent=2)

print(f"✅ Created {len(annotations)} annotations in {output_json}")



# import torch
# db = torch.load("D:/Fishing-AI/fishai_backend/cache/models/embedding_database.pt", map_location="cpu")

# ids = db[1] if isinstance(db, tuple) else db['ids']
# unique_ids = set(ids if isinstance(ids[0], int) else [x[0] for x in ids])
# print(f"Unique class IDs in database: {len(unique_ids)}")
