"""
Configuration for model files stored in Google Drive
"""

# Google Drive file IDs or URLs for your model files
# You can get file IDs from Google Drive sharing URLs
# Example: https://drive.google.com/file/d/1ABC123DEF456GHI789JKL012MNO345PQR/view
# File ID would be: 1ABC123DEF456GHI789JKL012MNO345PQR

MODEL_URLS = {
    "classification_model.ts": "https://drive.google.com/file/d/1ma8Og-vJGz7hAMyI3vJFRRC-FU4qtNJQ/view?usp=drive_link",
    "embedding_database.pt": "https://drive.google.com/file/d/1EY4WDqKKdpXTYf4tD0SJjDWtSZZiYwB5/view?usp=drive_link", 
    "segmentation_model.ts": "https://drive.google.com/file/d/1l4g_po7tVebvbSPpCMEvx9xl9PCDMFX7/view?usp=drive_link",
    "categories.json": "https://drive.google.com/file/d/1VXL3T9QonhK0io7PnT910PnrTCBsEL7p/view?usp=drive_link"
}

# Alternative: Use file IDs directly (recommended for better performance)
MODEL_FILE_IDS = {
    "classification_model.ts": "1ma8Og-vJGz7hAMyI3vJFRRC-FU4qtNJQ",
    "embedding_database.pt": "1EY4WDqKKdpXTYf4tD0SJjDWtSZZiYwB5", 
    "segmentation_model.ts": "1l4g_po7tVebvbSPpCMEvx9xl9PCDMFX7",
    "categories.json": "1VXL3T9QonhK0io7PnT910PnrTCBsEL7p"
}

# Cache configuration
CACHE_DIR = "cache/models"

# Model loading configuration
DEVICE = "cpu"  # Change to "cuda" if GPU available

# Google Drive API configuration
GOOGLE_DRIVE_CONFIG = {
    "scopes": ["https://www.googleapis.com/auth/drive.readonly"],
    "credentials_file": "cache/models/credentials.json",
    "token_file": "cache/models/token.pickle"
}

def get_model_urls():
    """Get model URLs configuration"""
    return MODEL_URLS

def get_model_file_ids():
    """Get model file IDs configuration"""
    return MODEL_FILE_IDS

def get_cache_dir():
    """Get cache directory path"""
    return CACHE_DIR

def get_device():
    """Get device configuration for model loading"""
    return DEVICE

def get_google_drive_config():
    """Get Google Drive API configuration"""
    return GOOGLE_DRIVE_CONFIG 