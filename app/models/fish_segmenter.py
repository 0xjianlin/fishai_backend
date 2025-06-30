import torch
import numpy as np
import cv2
import logging
import time
from PIL import Image
from shapely.geometry import Polygon
from torch.nn import functional as F

class FishSegmenter:
    """
    Simplified fish segmenter for FastAPI integration
    """
    
    def __init__(self, model_path, device='cpu'):
        start_time = time.time()
        self.device = device
        
        # Load model
        self.model = torch.jit.load(model_path, map_location=device)
        self.model.eval()
        
        # Default parameters
        self.min_size = 800
        self.max_size = 1333
        self.score_threshold = 0.3
        self.mask_threshold = 0.5
        self.nms_threshold = 0.9
        
        elapsed = time.time() - start_time
        logging.info(f"Fish segmenter loaded successfully in {elapsed:.2f} seconds")
    
    def segment(self, image_np):
        """
        Segment fish from image
        
        Args:
            image_np: numpy array of image (H, W, C)
            
        Returns:
            tuple: (polygons, masks) - list of polygon coordinates and binary masks
        """
        # Resize image
        resized_img, scales = self._resize_image(image_np)
        
        # Convert to tensor
        img_tensor = torch.as_tensor(resized_img.astype("float32").transpose(2, 0, 1))
        
        # Run inference
        with torch.no_grad():
            segm_output = self.model(img_tensor)
        
        # Process output
        masks_and_polygons = self._convert_output_to_masks_and_polygons(
            segm_output, resized_img, scales
        )
        
        # Apply NMS and filter
        polygons, masks = self._process_output(masks_and_polygons)
        
        return polygons, masks
    
    def _resize_image(self, image_np):
        """Resize image maintaining aspect ratio"""
        h, w = image_np.shape[:2]
        
        # Calculate new dimensions
        scale = self.min_size / min(h, w)
        new_h, new_w = int(h * scale), int(w * scale)
        
        if max(new_h, new_w) > self.max_size:
            scale = self.max_size / max(new_h, new_w)
            new_h, new_w = int(new_h * scale), int(new_w * scale)
        
        # Resize image
        resized = cv2.resize(image_np, (new_w, new_h))
        
        # Calculate scales for coordinate conversion
        scales = np.array([h / new_h, w / new_w])
        
        return resized, scales
    
    def _convert_output_to_masks_and_polygons(self, mask_rcnn_output, resized_img, scales):
        """Convert model output to masks and polygons"""
        boxes, classes, masks, scores, img_size = mask_rcnn_output
        # Ensure all outputs are tensors, not tuples
        if isinstance(boxes, tuple):
            boxes = boxes[0]
        if isinstance(classes, tuple):
            classes = classes[0]
        if isinstance(masks, tuple):
            masks = masks[0]
        if isinstance(scores, tuple):
            scores = scores[0]
        if isinstance(img_size, tuple):
            img_size = img_size[0]
        
        processed = []
        
        for i in range(len(masks)):
            if scores[i] <= self.score_threshold:
                continue
                
            # Ensure boxes[i] is a tensor or list of numbers, then convert to ints
            if isinstance(boxes[i], torch.Tensor):
                x1, y1, x2, y2 = [int(v) for v in boxes[i].tolist()]
            else:
                x1, y1, x2, y2 = [int(v) for v in boxes[i]]
            mask_h, mask_w = y2 - y1, x2 - x1
            
            # Extract mask
            mask = masks[i, 0, :, :]
            mask = self._paste_mask(mask.unsqueeze(0).unsqueeze(0), mask_h, mask_w).numpy()[0][0]
            
            # Threshold mask
            mask = np.where(mask > self.mask_threshold, 255, 0).astype(np.uint8)
            
            # Find contours
            contours = self._bitmap_to_polygon(mask)
            
            if len(contours) < 1:
                continue
            
            # Convert to original image coordinates
            polygon = self._rescale_polygon_to_src_size(contours[0], (x1, y1), scales)
            
            processed.append([mask, polygon])
        
        return processed
    
    def _process_output(self, output):
        """Apply NMS and filter results"""
        # Create polygon instances
        poly_instances = []
        for mask, polygon_array in output:
            try:
                poly = Polygon(polygon_array)
                poly_instances.append([poly, polygon_array, mask])
            except Exception as e:
                logging.warning(f"Invalid polygon: {e}")
                continue
        
        # Sort by area (largest first)
        poly_instances.sort(key=lambda x: x[0].area, reverse=True)
        
        # Apply NMS
        keep_indices = [0]
        for i in range(1, len(poly_instances)):
            keep = True
            for j in keep_indices:
                if self._calculate_iou(poly_instances[i][0], poly_instances[j][0]) > self.nms_threshold:
                    keep = False
                    break
            if keep:
                keep_indices.append(i)
        
        # Extract results
        polygons = [self._poly_array_to_dict(poly_instances[i][1]) for i in keep_indices]
        masks = [poly_instances[i][2] for i in keep_indices]
        
        return polygons, masks
    
    def _paste_mask(self, masks, img_h, img_w):
        """Paste mask to image size"""
        device = masks.device
        masks = F.interpolate(masks, size=(img_h, img_w), mode='bilinear', align_corners=False)
        return masks
    
    def _bitmap_to_polygon(self, bitmap):
        """Convert bitmap to polygon contours"""
        contours, _ = cv2.findContours(bitmap, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [contour.reshape(-1, 2).tolist() for contour in contours]
    
    def _rescale_polygon_to_src_size(self, poly, start_point, scales):
        """Rescale polygon to original image size"""
        return [[int((start_point[0] + point[0]) * scales[0]), 
                int((start_point[1] + point[1]) * scales[1])] for point in poly]
    
    def _poly_array_to_dict(self, poly):
        """Convert polygon array to dictionary format"""
        result = {}
        for i, point in enumerate(poly):
            result[f"x{i+1}"] = point[0]
            result[f"y{i+1}"] = point[1]
        return result
    
    def _calculate_iou(self, poly_a, poly_b):
        """Calculate IoU between two polygons"""
        intersection_area = poly_a.intersection(poly_b).area
        union_area = poly_a.union(poly_b).area
        return intersection_area / union_area if union_area > 0 else 0 