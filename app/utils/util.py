import cv2
import numpy as np

def extract_fish_region(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Extract fish region using segmentation mask"""
    # Ensure mask is uint8 and same size as image
    if mask.dtype != np.uint8:
        mask = mask.astype(np.uint8)
    if mask.shape[:2] != image.shape[:2]:
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
    # Apply mask to image
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    
    # Find bounding box of mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image  # Return full image if no contours found
    
    # Get largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Extract region with some padding
    padding = 10
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(image.shape[1], x + w + padding)
    y2 = min(image.shape[0], y + h + padding)
    
    return image[y1:y2, x1:x2]