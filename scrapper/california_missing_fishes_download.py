import os
import pandas as pd
import requests
from urllib.parse import urlparse
import glob
import base64
import re

# Configuration
EXCEL_DIR = "D:/california-missing-fishes"  # Directory containing Excel files
OUTPUT_BASE_DIR = "D:/california-missing-fishes"  # Base directory for downloaded images
MAX_IMAGES_PER_FILE = 100
IMG_URL_COL = 'YQ4gaf src'
SPECIES_NAME_COL = 'toI8Rb'

def get_file_extension(url):
    """Extract file extension from URL"""
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext if ext else '.jpg'

def sanitize_filename(name):
    """Remove invalid characters from filename"""
    return ''.join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()

def download_image(url, filepath):
    """Download image from URL or save base64 image to filepath"""
    try:
        if url.startswith('data:image/'):
            # Extract extension and base64 data
            match = re.match(r'data:image/(.*?);base64,(.*)', url)
            if not match:
                print(f"Invalid base64 image data: {url[:30]}...")
                return False
            ext, b64data = match.groups()
            ext = '.' + ext.split('+')[0]  # handle e.g. image/jpeg+xyz
            filepath = os.path.splitext(filepath)[0] + ext
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(b64data))
            return True
        else:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"Failed to download {url} (status: {response.status_code})")
                return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def process_excel_file(excel_path):
    """Process a single Excel file"""
    # Get Excel filename without extension
    excel_filename = os.path.splitext(os.path.basename(excel_path))[0]
    print(f"\nProcessing Excel file: {excel_filename}")
    
    # Create subdirectory for this Excel file (exact name as xlsx file, no extension)
    subdir = os.path.join(OUTPUT_BASE_DIR, excel_filename)
    os.makedirs(subdir, exist_ok=True)
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        print(f"Found {len(df)} rows in {excel_filename}")
        
        # Check if required columns exist
        if IMG_URL_COL not in df.columns:
            print(f"Column '{IMG_URL_COL}' not found in {excel_filename}")
            return
        if SPECIES_NAME_COL not in df.columns:
            print(f"Column '{SPECIES_NAME_COL}' not found in {excel_filename}")
            return
        
        downloaded_count = 0
        
        for idx, row in df.iterrows():
            if downloaded_count >= MAX_IMAGES_PER_FILE:
                print(f"Reached maximum images ({MAX_IMAGES_PER_FILE}) for {excel_filename}")
                break
                
            img_url = row.get(IMG_URL_COL)
            species_name = row.get(SPECIES_NAME_COL)
            
            # Skip if data is missing
            if not isinstance(img_url, str) or not isinstance(species_name, str):
                continue
                
            # Check if species name contains Excel filename
            if excel_filename.lower() not in species_name.lower():
                continue
                
            # Generate filename: 1.jpg, 2.png, ...
            ext = get_file_extension(img_url)
            file_number = downloaded_count + 1
            filename = f"{file_number}{ext}"
            filepath = os.path.join(subdir, filename)
            
            # Skip if file already exists
            if os.path.exists(filepath):
                print(f"File already exists: {filename}")
                continue
                
            # Download image
            print(f"Downloading {file_number}: {species_name}")
            if download_image(img_url, filepath):
                downloaded_count += 1
                print(f"Successfully downloaded: {filename}")
            else:
                print(f"Failed to download: {species_name}")
        
        print(f"Downloaded {downloaded_count} images for {excel_filename}")
        
    except Exception as e:
        print(f"Error processing {excel_filename}: {e}")

def main():
    """Main function to process all Excel files"""
    print("Starting California Missing Fishes Image Download")
    print("=" * 50)
    
    # Find all Excel files in the directory
    excel_files = glob.glob(os.path.join(EXCEL_DIR, "*.xlsx"))
    excel_files.extend(glob.glob(os.path.join(EXCEL_DIR, "*.xls")))
    
    if not excel_files:
        print(f"No Excel files found in {EXCEL_DIR}")
        return
    
    print(f"Found {len(excel_files)} Excel files")
    
    # Process each Excel file
    for excel_file in excel_files:
        process_excel_file(excel_file)
    
    print("\n" + "=" * 50)
    print("Download process completed!")

if __name__ == "__main__":
    main() 