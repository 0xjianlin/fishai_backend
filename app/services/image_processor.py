import cv2
import numpy as np
from PIL import Image
import io
from ..utils.config import settings
from typing import Union, Tuple

def process_image(image_data: bytes) -> bytes:
    """
    Process uploaded image for model input
    - Resize to model input size
    - Normalize pixel values
    - Convert to RGB if needed
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image")
        
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize image while maintaining aspect ratio
        max_size = settings.MAX_IMAGE_SIZE
        height, width = img.shape[:2]
        
        if height > max_size or width > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Convert to PIL Image for further processing
        pil_img = Image.fromarray(img)
        
        # Convert back to bytes
        img_byte_arr = io.BytesIO()
        pil_img.save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr = img_byte_arr.getvalue()
        
        return img_byte_arr
    
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")

def preprocess_for_model(image_data: bytes) -> np.ndarray:
    """
    Preprocess image data for the fish identification model
    Args:
        image_data: Raw image bytes
    Returns:
        Preprocessed image as numpy array
    """
    # Convert bytes to image
    image = Image.open(io.BytesIO(image_data))
    
    # Convert to RGB if needed (for model compatibility)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize image to model input size
    image = image.resize((224, 224))  # Standard size for many CNN models
    
    # Convert to numpy array and normalize
    image_array = np.array(image) / 255.0
    
    # Add batch dimension
    image_array = np.expand_dims(image_array, axis=0)
    
    return image_array

def validate_image(image_data: bytes) -> Tuple[bool, str]:
    """
    Validate if the uploaded image is suitable for processing
    Args:
        image_data: Raw image bytes
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Try to open the image
        image = Image.open(io.BytesIO(image_data))
        
        # Accept all common formats supported by Pillow
        supported_formats = ['JPEG', 'JPG', 'PNG', 'WEBP', 'BMP', 'GIF', 'TIFF']
        if image.format not in supported_formats:
            return False, f"Only these image formats are supported: {', '.join(supported_formats)}"
        
        # Check image size
        if image.size[0] < 100 or image.size[1] < 100:
            return False, "Image is too small. Minimum size is 100x100 pixels"
        
        # Check if image is corrupted
        image.verify()
        
        return True, ""
        
    except Exception as e:
        return False, f"Invalid image: {str(e)}"

def enhance_image(image_data: bytes) -> bytes:
    """
    Apply basic image enhancement to improve fish detection
    Args:
        image_data: Raw image bytes
    Returns:
        Enhanced image as bytes
    """
    # Convert bytes to OpenCV format
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Convert to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    
    # Merge channels
    enhanced_lab = cv2.merge((cl, a, b))
    
    # Convert back to BGR
    enhanced_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    # Convert back to bytes
    _, buffer = cv2.imencode('.jpg', enhanced_img)
    return buffer.tobytes() 