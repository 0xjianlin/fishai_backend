import os
import requests
import pandas as pd
from urllib.parse import urlparse

EXCEL_PATH = 'D:/Fishing-AI/fishai_backend/references/identify/all-fisheries-3.xlsx'
OUTPUT_DIR = 'D:/fish_images'
IMG_URL_COL = 'img-responsive src'
COMMON_NAME_COL = 'bold-font'

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_file_extension(url):
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext if ext else '.jpg'

def sanitize_filename(name):
    # Remove characters not allowed in filenames
    return ''.join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()

def main():
    df = pd.read_excel(EXCEL_PATH)
    for idx, row in df.iterrows():
        img_url = row.get(IMG_URL_COL)
        common_name = row.get(COMMON_NAME_COL)
        if not isinstance(img_url, str) or not isinstance(common_name, str):
            print(f"Skipping row {idx}: missing data.")
            continue
        ext = get_file_extension(img_url)
        filename = f"{sanitize_filename(common_name)}{ext}"
        out_path = os.path.join(OUTPUT_DIR, filename)
        try:
            resp = requests.get(img_url, timeout=10)
            if resp.status_code == 200:
                with open(out_path, 'wb') as f:
                    f.write(resp.content)
                print(f"Downloaded: {filename}")
            else:
                print(f"Failed to download {img_url} (status {resp.status_code})")
        except Exception as e:
            print(f"Error downloading {img_url}: {e}")

if __name__ == '__main__':
    main()