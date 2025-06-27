#!/usr/bin/env python3
"""
Simplified setup script for Google Drive integration using gdown
This script helps you configure and test the gdown model download functionality
"""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.simple_model_manager import SimpleModelManager
from app.utils.model_config import get_model_urls, get_cache_dir

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'gdown',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def configure_model_urls():
    """Help user configure model URLs"""
    config_path = Path("app/utils/model_config.py")
    
    print("\n📝 Model URL Configuration")
    print("You need to update the model URLs in the configuration file.")
    print(f"Edit: {config_path}")
    print("\nTo get sharing URLs from Google Drive:")
    print("1. Upload your model files to Google Drive")
    print("2. Right-click on each file and select 'Share'")
    print("3. Click 'Copy link'")
    print("4. Make sure the link is set to 'Anyone with the link can view'")
    
    current_config = get_model_urls()
    print("\nCurrent configuration:")
    for filename, url in current_config.items():
        status = "✅" if "drive.google.com" in url else "❌"
        print(f"   {status} {filename}: {url}")
    
    return all("drive.google.com" in url for url in current_config.values())

def test_model_download():
    """Test downloading models from Google Drive"""
    print("\n🧪 Testing Model Download")
    
    try:
        model_manager = SimpleModelManager(get_cache_dir())
        model_urls = get_model_urls()
        
        # Check if URLs are configured
        if not all("drive.google.com" in url for url in model_urls.values()):
            print("❌ Model URLs not configured. Please update the configuration first.")
            return False
        
        print("Downloading models from Google Drive using gdown...")
        success = model_manager.setup_models_from_urls(model_urls)
        
        if success:
            print("✅ All models downloaded successfully!")
            
            # Show model info
            model_info = model_manager.get_model_info()
            print("\n📊 Model Information:")
            for filename, info in model_info["models"].items():
                if info["downloaded"]:
                    print(f"   ✅ {filename}: {info['file_size_mb']} MB")
                else:
                    print(f"   ❌ {filename}: Not downloaded")
            
            return True
        else:
            print("❌ Failed to download some models")
            return False
            
    except Exception as e:
        print(f"❌ Error during model download: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Google Drive Model Setup (gdown)")
    print("=" * 50)
    print("Using gdown - no Google Cloud credentials required!")
    print("=" * 50)
    
    setup_logging()
    
    # Check requirements
    if not check_requirements():
        return
    
    # Configure URLs
    if not configure_model_urls():
        print("\n⚠️  Please configure the model URLs before proceeding")
        return
    
    # Test download
    if test_model_download():
        print("\n🎉 Setup completed successfully!")
        print("Your models are now ready to use with the FastAPI application.")
        print("\n💡 Benefits of using gdown:")
        print("   - No Google Cloud setup required")
        print("   - Works with public sharing links")
        print("   - Simpler configuration")
        print("   - Fewer dependencies")
    else:
        print("\n❌ Setup failed. Please check the configuration and try again.")

if __name__ == "__main__":
    main() 