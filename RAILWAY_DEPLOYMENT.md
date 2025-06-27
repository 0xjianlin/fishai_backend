# Railway Deployment Guide

This guide will help you deploy the Fishing-AI API to Railway without the OpenCV `libGL.so.1` error.

## Changes Made for Railway Deployment

### 1. Fixed OpenCV Issue
- **Problem**: `opencv-python` requires GUI libraries (`libGL.so.1`) that aren't available in Railway's headless environment
- **Solution**: Replaced `opencv-python` with `opencv-python-headless` in `requirements.txt`

### 2. Added Railway Configuration
- Created `railway.json` with proper build and deployment settings
- Added health check endpoint configuration
- Set restart policy for better reliability

### 3. Created Dockerfile (Alternative)
- Provides complete control over the deployment environment
- Installs all necessary system dependencies
- Includes proper health checks

### 4. Enhanced Startup Script
- Created `startup.py` with better error handling
- Graceful model download handling
- Dependency verification
- Production-ready configuration

## Deployment Options

### Option 1: Railway Native Deployment (Recommended)

1. **Connect your repository to Railway**
   - Go to Railway Dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Railway will automatically detect the configuration**
   - Uses `railway.json` for build settings
   - Uses `startup.py` as the start command
   - Uses `/health` endpoint for health checks

3. **Environment Variables** (if needed)
   - Railway automatically provides `PORT` environment variable
   - Add any additional environment variables in Railway dashboard

### Option 2: Docker Deployment

1. **Railway will automatically detect the Dockerfile**
   - Uses Docker build process
   - Installs all system dependencies
   - More reliable but slower builds

2. **Manual Docker deployment**
   ```bash
   # Build the image
   docker build -t fishai-api .
   
   # Run locally
   docker run -p 8000:8000 fishai-api
   ```

## Key Features

### Health Check Endpoint
- **URL**: `/health`
- **Purpose**: Railway uses this to monitor application health
- **Response**: JSON with status and model loading information

### Model Download
- Models are downloaded from Google Drive on first startup
- Uses `gdown` library (no authentication required)
- Cached locally for subsequent requests
- Graceful fallback if download fails

### Error Handling
- Startup script checks dependencies before starting
- Model download failures don't crash the application
- Proper logging for debugging

## Troubleshooting

### Common Issues

1. **OpenCV Error**: Already fixed by using `opencv-python-headless`

2. **Model Download Failures**:
   - Check Google Drive links are accessible
   - Verify internet connectivity in Railway environment
   - Models will be downloaded on first API request

3. **Memory Issues**:
   - Railway provides limited memory
   - Models are loaded on-demand
   - Consider upgrading Railway plan if needed

4. **Port Issues**:
   - Application automatically uses Railway's `PORT` environment variable
   - No manual port configuration needed

### Monitoring

1. **Railway Dashboard**:
   - Monitor deployment status
   - View logs in real-time
   - Check resource usage

2. **Application Logs**:
   - Startup script provides detailed logging
   - FastAPI logs are also available
   - Use Railway's log viewer

## Performance Considerations

1. **Cold Starts**: First request may be slower due to model loading
2. **Memory Usage**: Models are kept in memory after loading
3. **Concurrent Requests**: FastAPI handles multiple requests efficiently

## Security

1. **CORS**: Configured for your frontend domains
2. **Input Validation**: FastAPI provides automatic validation
3. **Error Messages**: Sensitive information is not exposed in errors

## Next Steps

1. Deploy to Railway using the provided configuration
2. Test the health endpoint: `https://your-app.railway.app/health`
3. Test the API documentation: `https://your-app.railway.app/docs`
4. Integrate with your frontend application

## Support

If you encounter issues:
1. Check Railway logs for detailed error messages
2. Verify all files are committed to your repository
3. Ensure Google Drive links are accessible
4. Contact Railway support if needed 