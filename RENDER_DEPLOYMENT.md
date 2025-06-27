# 🚀 Deploy to Render - Quick Guide

## Prerequisites ✅
- ✅ GitHub repository with your code pushed
- ✅ Render account (free at [render.com](https://render.com))

## Step 1: Connect to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account if not already connected
4. Select your repository: `fishai_backend`

## Step 2: Deploy

1. Render will automatically detect your `render.yaml` configuration
2. Click **"Apply"** to start deployment
3. Wait for the build to complete (5-10 minutes for first deployment)

## Step 3: Your API is Live! 🎉

Your API will be available at:
- **Main URL**: `https://fishai-backend.onrender.com`
- **API Documentation**: `https://fishai-backend.onrender.com/docs`
- **Health Check**: `https://fishai-backend.onrender.com/health`

## 🔧 What Happens During Deployment

1. **Build Phase**: 
   - Installs Python dependencies from `requirements.txt`
   - Downloads model files from Google Drive using gdown
   - Caches models in `cache/models/` directory

2. **Start Phase**:
   - Starts FastAPI server with uvicorn
   - Loads fish classification and segmentation models
   - API becomes available

## 📊 Monitoring

- **Logs**: Check deployment logs in Render Dashboard
- **Health**: Visit `/health` endpoint to check model status
- **Auto-deploy**: Changes to main branch automatically trigger new deployments

## 🐛 Troubleshooting

### Build Fails
- Check logs for missing dependencies
- Verify `requirements.txt` is up to date
- Ensure all files are committed to GitHub

### Models Not Loading
- Check `/health` endpoint for model status
- Verify Google Drive URLs in `app/utils/model_config.py`
- Check logs for download errors

### Memory Issues
- Free tier has 512MB RAM limit
- Large model files may cause issues
- Consider upgrading to paid plan if needed

## 🔄 Continuous Deployment

- Every push to `main` branch triggers automatic deployment
- No manual intervention needed
- Deployment takes 2-3 minutes for updates

## 💰 Cost

- **Free Tier**: 750 hours/month, 512MB RAM
- **Perfect for**: Development, testing, small-scale production
- **Upgrade when**: You need more RAM or faster performance

## 🎯 Next Steps

1. **Test your API**: Try the `/docs` endpoint
2. **Update CORS**: If you have a frontend, update CORS settings
3. **Monitor**: Check logs and health endpoint regularly
4. **Scale**: Upgrade to paid plan if needed

## 📞 Support

- **Render Support**: [help.render.com](https://help.render.com)
- **Your API**: Check `/health` for status
- **Logs**: Available in Render Dashboard 