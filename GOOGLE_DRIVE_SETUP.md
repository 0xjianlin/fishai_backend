# Google Drive Integration Setup Guide

This guide will help you set up Google Drive integration to store and download your model files (`classification_model.ts`, `embedding_database.pt`, `segmentation_model.ts`) from Google Drive.

## Overview

The application now supports downloading model files from Google Drive instead of storing them locally. This is useful for:
- Reducing repository size
- Sharing models across different deployments
- Automatic model updates
- Better version control

## Prerequisites

1. **Google Cloud Project**: You need a Google Cloud project with the Google Drive API enabled
2. **OAuth 2.0 Credentials**: API credentials for accessing Google Drive
3. **Model Files**: Your model files uploaded to Google Drive

## Step 1: Set Up Google Cloud Project

### 1.1 Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 1.2 Enable Google Drive API
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click on it and press "Enable"

### 1.3 Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "FishAI Model Downloader")
5. Click "Create"
6. Download the JSON credentials file

### 1.4 Save Credentials
1. Create the cache directory: `mkdir -p cache/models`
2. Save the downloaded JSON file as `cache/models/credentials.json`

## Step 2: Upload Model Files to Google Drive

### 2.1 Upload Files
1. Go to [Google Drive](https://drive.google.com/)
2. Create a new folder for your models (optional but recommended)
3. Upload your model files:
   - `classification_model.ts`
   - `embedding_database.pt`
   - `segmentation_model.ts`
   - `categories.json`

### 2.2 Get File IDs
For each file:
1. Right-click on the file in Google Drive
2. Select "Share"
3. Click "Copy link"
4. Extract the file ID from the URL

**Example:**
- URL: `https://drive.google.com/file/d/1ABC123DEF456GHI789JKL012MNO345PQR/view`
- File ID: `1ABC123DEF456GHI789JKL012MNO345PQR`

## Step 3: Configure the Application

### 3.1 Update Model Configuration
Edit `app/utils/model_config.py` and replace the placeholder file IDs:

```python
MODEL_FILE_IDS = {
    "classification_model.ts": "YOUR_ACTUAL_CLASSIFICATION_MODEL_FILE_ID",
    "embedding_database.pt": "YOUR_ACTUAL_EMBEDDING_DATABASE_FILE_ID", 
    "segmentation_model.ts": "YOUR_ACTUAL_SEGMENTATION_MODEL_FILE_ID",
    "categories.json": "YOUR_ACTUAL_CATEGORIES_FILE_ID"
}
```

### 3.2 Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 4: Test the Setup

### 4.1 Run the Setup Script
```bash
python setup_google_drive.py
```

This script will:
- Check if all required packages are installed
- Verify Google Drive credentials
- Test downloading models from Google Drive
- Show model information

### 4.2 Manual Testing
You can also test the setup manually:

```python
from app.services.model_manager import ModelManager
from app.utils.model_config import get_model_file_ids, get_cache_dir

# Initialize model manager
model_manager = ModelManager(get_cache_dir())

# Download models
model_file_ids = get_model_file_ids()
success = model_manager.setup_models_from_file_ids(model_file_ids)

if success:
    print("✅ Models downloaded successfully!")
    print(model_manager.get_model_info())
else:
    print("❌ Failed to download models")
```

## Step 5: Run the Application

### 5.1 Start the FastAPI Application
```bash
python run.py
```

The application will automatically:
1. Download models from Google Drive on startup
2. Cache them locally for faster subsequent loads
3. Initialize the fish classifier and segmenter

### 5.2 Verify Models are Loaded
Check the health endpoint:
```bash
curl http://localhost:8000/health
```

Or visit: `http://localhost:8000/models/info`

## API Endpoints

The application now includes new endpoints for model management:

- `GET /health` - Health check with model status
- `GET /models/info` - Detailed model information
- `POST /models/refresh` - Force refresh models from Google Drive

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
**Problem**: "Failed to authenticate with Google Drive API"
**Solution**: 
- Verify `credentials.json` is in the correct location
- Check that the Google Drive API is enabled
- Ensure the credentials are for a desktop application

#### 2. File Not Found Errors
**Problem**: "Failed to download model file"
**Solution**:
- Verify file IDs are correct
- Ensure files are shared with "Anyone with the link can view"
- Check file permissions in Google Drive

#### 3. Permission Errors
**Problem**: "Access denied" or "Forbidden"
**Solution**:
- Make sure files are publicly accessible or shared properly
- Check OAuth scopes in credentials
- Verify the Google account has access to the files

#### 4. Network Issues
**Problem**: "Connection timeout" or "Network error"
**Solution**:
- Check internet connection
- Verify firewall settings
- Try using a different network

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Manual File Download

If automatic download fails, you can manually download files:

```python
from app.services.google_drive_service import GoogleDriveService

drive_service = GoogleDriveService()
file_path = drive_service.download_file_by_id("YOUR_FILE_ID", "filename.ext")
```

## Security Considerations

1. **Credentials Security**: Keep your `credentials.json` file secure and don't commit it to version control
2. **File Permissions**: Only share files that need to be publicly accessible
3. **API Quotas**: Be aware of Google Drive API quotas and limits
4. **Caching**: Downloaded files are cached locally for performance

## Performance Optimization

1. **Caching**: Models are cached locally after first download
2. **Parallel Downloads**: Multiple models can be downloaded simultaneously
3. **Resume Support**: Downloads can be resumed if interrupted
4. **Compression**: Consider compressing large model files before uploading

## Backup Strategy

1. **Multiple Sources**: Consider having backup model files in different locations
2. **Version Control**: Keep track of model versions and file IDs
3. **Local Backup**: Keep local copies of critical model files
4. **Monitoring**: Set up alerts for model download failures

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the application logs
3. Test with the setup script
4. Verify Google Drive API quotas and limits 