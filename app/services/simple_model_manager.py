import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
from .gdown_service import GDownService

class SimpleModelManager:
    """
    Simplified model manager using gdown for Google Drive downloads
    """
    
    def __init__(self, cache_dir: str = "cache/models"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.gdown_service = GDownService(cache_dir)
        
        # Model file configurations
        self.model_configs = {
            "classification_model.ts": {
                "description": "Fish classification model",
                "required": True
            },
            "embedding_database.pt": {
                "description": "Embedding database for classification",
                "required": True
            },
            "segmentation_model.ts": {
                "description": "Fish segmentation model",
                "required": True
            },
            "categories.json": {
                "description": "Species categories mapping",
                "required": True
            }
        }
        
        # Store file paths after download
        self.model_paths: Dict[str, Path] = {}
    
    def setup_models_from_urls(self, model_urls: Dict[str, str]) -> bool:
        """
        Download and setup all required model files from Google Drive URLs
        
        Args:
            model_urls: Dictionary mapping filename to Google Drive sharing URL
            
        Returns:
            True if all models were downloaded successfully
        """
        success = True
        
        for filename, url in model_urls.items():
            if filename not in self.model_configs:
                logging.warning(f"Unknown model file: {filename}")
                continue
            
            # Check if already cached
            cached_path = self.gdown_service.get_cached_file(filename)
            if cached_path:
                self.model_paths[filename] = cached_path
                logging.info(f"Using cached model: {filename}")
                continue
            
            # Download from Google Drive
            logging.info(f"Downloading model: {filename}")
            downloaded_path = self.gdown_service.download_file_from_url(url, filename)
            
            if downloaded_path:
                self.model_paths[filename] = downloaded_path
                logging.info(f"Successfully downloaded: {filename}")
            else:
                if self.model_configs[filename]["required"]:
                    logging.error(f"Failed to download required model: {filename}")
                    success = False
                else:
                    logging.warning(f"Failed to download optional model: {filename}")
        
        return success
    
    def setup_models_from_file_ids(self, model_file_ids: Dict[str, str]) -> bool:
        """
        Download and setup all required model files from Google Drive using file IDs
        
        Args:
            model_file_ids: Dictionary mapping filename to Google Drive file ID
            
        Returns:
            True if all models were downloaded successfully
        """
        success = True
        
        for filename, file_id in model_file_ids.items():
            if filename not in self.model_configs:
                logging.warning(f"Unknown model file: {filename}")
                continue
            
            # Check if already cached
            cached_path = self.gdown_service.get_cached_file(filename)
            if cached_path:
                self.model_paths[filename] = cached_path
                logging.info(f"Using cached model: {filename}")
                continue
            
            # Download from Google Drive
            logging.info(f"Downloading model: {filename}")
            downloaded_path = self.gdown_service.download_file_from_id(file_id, filename)
            
            if downloaded_path:
                self.model_paths[filename] = downloaded_path
                logging.info(f"Successfully downloaded: {filename}")
            else:
                if self.model_configs[filename]["required"]:
                    logging.error(f"Failed to download required model: {filename}")
                    success = False
                else:
                    logging.warning(f"Failed to download optional model: {filename}")
        
        return success
    
    def get_model_path(self, filename: str) -> Optional[Path]:
        """
        Get the local path of a downloaded model file
        
        Args:
            filename: Name of the model file
            
        Returns:
            Path to the model file or None if not found
        """
        return self.model_paths.get(filename)
    
    def get_all_model_paths(self) -> Dict[str, Path]:
        """
        Get all downloaded model file paths
        
        Returns:
            Dictionary mapping filename to file path
        """
        return self.model_paths.copy()
    
    def verify_models(self) -> bool:
        """
        Verify that all required model files are available
        
        Returns:
            True if all required models are available
        """
        missing_models = []
        
        for filename, config in self.model_configs.items():
            if config["required"] and filename not in self.model_paths:
                missing_models.append(filename)
        
        if missing_models:
            logging.error(f"Missing required model files: {missing_models}")
            return False
        
        # Verify files exist
        for filename, file_path in self.model_paths.items():
            if not file_path.exists():
                logging.error(f"Model file not found: {filename} at {file_path}")
                return False
        
        logging.info("All required models verified successfully")
        return True
    
    def clear_cache(self):
        """Clear all cached model files"""
        self.gdown_service.clear_cache()
        self.model_paths.clear()
        logging.info("Model cache cleared")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about all model files
        
        Returns:
            Dictionary with model information
        """
        info = {
            "cache_directory": str(self.cache_dir),
            "download_method": "gdown",
            "models": {}
        }
        
        for filename, config in self.model_configs.items():
            model_info = {
                "description": config["description"],
                "required": config["required"],
                "downloaded": filename in self.model_paths,
                "path": str(self.model_paths.get(filename, "Not downloaded"))
            }
            
            if filename in self.model_paths and self.model_paths[filename].exists():
                model_info["file_size"] = self.model_paths[filename].stat().st_size
                model_info["file_size_mb"] = round(model_info["file_size"] / (1024 * 1024), 2)
            
            info["models"][filename] = model_info
        
        return info 