import cloudinary
import cloudinary.uploader
import os
import json

# Cloudinary config
cloudinary.config(
  cloud_name = 'dtz92sayc',
  api_key = '164218739949581',
  api_secret = 'GCAXRiLlndXOTPdHcPmNG8Mcfvw'
)

IMAGES_DIR = 'D:/fish_images'
OUTPUT_JSON = 'D:/Fishing-AI/fishai_backend/models/classification/image_urls.json'

image_urls = {}

for filename in os.listdir(IMAGES_DIR):
    common_name = os.path.splitext(filename)[0]
    file_path = os.path.join(IMAGES_DIR, filename)
    print(f"Uploading {filename}...")
    try:
        result = cloudinary.uploader.upload(file_path, folder="fish_images")
        url = result['secure_url']
        image_urls[common_name] = url
        print(f"Uploaded: {common_name} -> {url}")
    except Exception as e:
        print(f"Failed to upload {filename}: {e}")

# Save to JSON
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(image_urls, f, indent=2, ensure_ascii=False)

print(f"All URLs saved to {OUTPUT_JSON}")