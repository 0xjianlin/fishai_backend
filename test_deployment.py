#!/usr/bin/env python3
"""
Test script to verify deployment readiness
Run this before deploying to Render
"""

import sys
import os
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'cv2',
        'numpy',
        'PIL',
        'torch',
        'torchvision',
        'cloudinary',
        'shapely',
        'pydantic',
        'requests'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {failed_imports}")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_app_startup():
    """Test if the FastAPI app can start"""
    print("\n🚀 Testing app startup...")
    
    try:
        # Import the app
        from app.main import app
        print("✅ App imported successfully")
        
        # Test if models can be loaded (this might take time)
        print("⏳ Testing model loading...")
        from app.state import classifier, segmenter
        
        # Note: Models might not be loaded in test environment
        print("✅ App startup test completed")
        return True
        
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False

def test_file_structure():
    """Test if required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'requirements.txt',
        'render.yaml',
        'app/main.py',
        'app/api/identify.py',
        'models/classification/classification_model.ts',
        'models/classification/segmentation_model.ts',
        'models/classification/categories.json'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print("\n✅ All required files found!")
        return True

def main():
    """Run all tests"""
    print("🧪 FishAI Backend - Deployment Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_file_structure,
        test_app_startup
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    if all(results):
        print("🎉 All tests passed! Your app is ready for deployment.")
        print("\nNext steps:")
        print("1. Push your code to GitHub")
        print("2. Go to Render Dashboard")
        print("3. Create new Web Service")
        print("4. Connect your GitHub repo")
        print("5. Deploy!")
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        print("\nCommon fixes:")
        print("- Run: pip install -r requirements.txt")
        print("- Check if all model files are present")
        print("- Verify file paths in app/main.py")

if __name__ == "__main__":
    main() 