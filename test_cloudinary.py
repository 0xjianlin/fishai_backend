#!/usr/bin/env python3
"""
Test script for Cloudinary integration
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.cloudinary_service import cloudinary_service
import numpy as np
from PIL import Image

def test_cloudinary_connection():
    """Test basic Cloudinary connection"""
    print("🧪 Testing Cloudinary Connection...")
    
    try:
        # Test listing images (should work even if no images exist)
        result = cloudinary_service.list_images(max_results=5)
        
        if result.get('success'):
            print("✅ Cloudinary connection successful!")
            print(f"   Found {len(result.get('images', []))} images")
            return True
        else:
            print(f"❌ Cloudinary connection failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Cloudinary: {e}")
        return False

def test_image_upload():
    """Test image upload functionality"""
    print("\n📤 Testing Image Upload...")
    
    try:
        # Create a simple test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Test numpy image upload
        result = cloudinary_service.upload_numpy_image(
            test_image, "test_image.jpg", "fishai/test_upload"
        )
        
        if result.get('success'):
            print("✅ Image upload successful!")
            print(f"   URL: {result.get('url')}")
            print(f"   Public ID: {result.get('public_id')}")
            
            # Clean up - delete the test image
            delete_result = cloudinary_service.delete_image(result.get('public_id'))
            if delete_result.get('success'):
                print("✅ Test image deleted successfully")
            else:
                print("⚠️  Could not delete test image")
            
            return True
        else:
            print(f"❌ Image upload failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing image upload: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Cloudinary Integration Test")
    print("=" * 40)
    
    # Test connection
    connection_ok = test_cloudinary_connection()
    
    if connection_ok:
        # Test upload
        upload_ok = test_image_upload()
        
        if upload_ok:
            print("\n🎉 All Cloudinary tests passed!")
            print("Your Cloudinary integration is working correctly.")
        else:
            print("\n❌ Upload test failed.")
            print("Check your Cloudinary credentials and permissions.")
    else:
        print("\n❌ Connection test failed.")
        print("Check your Cloudinary credentials in config.py")

if __name__ == "__main__":
    main() 