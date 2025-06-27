# FishAI Backend - Render Deployment Guide

## 🚀 Quick Deploy to Render

### Prerequisites
- GitHub account with your code pushed
- Render account (free tier available)

### Step 1: Prepare Your Repository
1. Make sure your code is pushed to GitHub
2. Ensure `requirements.txt` and `render.yaml` are in the root directory
3. Verify your main app file is `app/main.py`

### Step 2: Deploy on Render

#### Option A: Using render.yaml (Recommended)
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` configuration
5. Click **"Apply"**

#### Option B: Manual Setup
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `fishai-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`

### Step 3: Environment Variables
Set these in Render Dashboard → Environment:
```
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
ENV=production
LOG_LEVEL=INFO
```

### Step 4: Wait for Deployment
- Build time: ~5-10 minutes (first time)
- Subsequent deployments: ~2-3 minutes

### Step 5: Test Your API
Your API will be available at:
- **Main URL**: `https://your-app-name.onrender.com`
- **API Docs**: `https://your-app-name.onrender.com/docs`
- **Health Check**: `https://your-app-name.onrender.com/`

## 🔧 Configuration Details

### CORS Settings
The app is configured for local development. For production, update CORS in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Model Loading
Models are loaded on startup. Ensure model files are included in your repository or stored externally.

## 🐛 Troubleshooting

### Common Issues:
1. **Build fails**: Check `requirements.txt` for missing dependencies
2. **Models not found**: Verify model file paths in `app/main.py`
3. **Memory issues**: Free tier has 512MB RAM limit
4. **Timeout**: Free tier has 15-minute timeout for requests

### Logs
Check deployment logs in Render Dashboard → Logs tab

## 📝 API Endpoints

- `GET /` - Health check
- `POST /api/identify` - Fish identification
- `GET /api/species` - List all species
- `GET /docs` - Interactive API documentation

## 🔄 Continuous Deployment
Render automatically redeploys when you push to your main branch.

## 💰 Costs
- **Free tier**: 750 hours/month, 512MB RAM
- **Paid plans**: Available for higher performance needs 