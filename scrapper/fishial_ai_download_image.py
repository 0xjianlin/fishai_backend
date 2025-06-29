import os
import json
import requests
import cloudinary
import cloudinary.uploader
from urllib.parse import urlparse
import time

# Cloudinary config
cloudinary.config(
    cloud_name='dtz92sayc',
    api_key='164218739949581',
    api_secret='GCAXRiLlndXOTPdHcPmNG8Mcfvw'
)

CATEGORIES_PATH = 'D:/Fishing-AI/fishai_backend/models/classification/categories.json'
OUTPUT_PATH = 'D:/Fishing-AI/fishai_backend/models/classification/categories_fishial_ai.json'
API_URL = 'https://searchapi.fishangler.com/fishspecies/search?searchText={}&saltWater=true&freshWater=true&brackishWater=true&numberOfItems=10'
TMP_IMG = 'tmp_fishial_ai.jpg'

# Load categories
with open(CATEGORIES_PATH, 'r', encoding='utf-8') as f:
    categories = json.load(f)

if 'categories' in categories:
    categories = categories['categories']

updated_categories = {}

for idx, info in categories.items():
    common_name = info.get('name')
    scientific_name = info.get('species_id')
    if not common_name:
        continue
    print(f"Processing: {common_name}")
    try:
        # Query FishAngler API
        url = API_URL.format(requests.utils.quote(common_name))
        resp = requests.get(url, timeout=10)
        data = resp.json()
        photo_url = None
        if 'result' in data and data['result']:
            for item in data['result']:
                if item.get('name', '').lower() == common_name.lower() or item.get('scientificName', '').lower() == scientific_name.lower():
                    photo_url = item.get('photoUri')
                    break
        if not photo_url:
            print(f"No image found for {common_name}")
            continue
        # Download image
        img_resp = requests.get(photo_url, timeout=10)
        if img_resp.status_code != 200:
            print(f"Failed to download image for {common_name}")
            continue
        with open(TMP_IMG, 'wb') as img_file:
            img_file.write(img_resp.content)
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(TMP_IMG, folder='fishial_ai', public_id=common_name.replace(' ', '_'))
        image_url = upload_result['secure_url']
        print(f"Uploaded to Cloudinary: {image_url}")
        # Update category
        updated_categories[idx] = {
            'name': common_name,
            'species_id': scientific_name,
            'image_url': image_url
        }
        # Be polite to the API
        time.sleep(1)
    except Exception as e:
        print(f"Error processing {common_name}: {e}")
        continue
# Remove temp image
if os.path.exists(TMP_IMG):
    os.remove(TMP_IMG)
# Save updated categories
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump({'categories': updated_categories}, f, indent=2, ensure_ascii=False)
print(f"Updated categories saved to {OUTPUT_PATH}")
