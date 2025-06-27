import os
import logging
import gdown
from pathlib import Path
from typing import Optional, Dict, Any
import requests

class GDownService:
    """
    Simplified service for downloading files from Google Drive using gdown
    """
    
    def __init__(self, cache_dir: str = "cache/models"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Store file paths after download
        self.downloaded_files: Dict[str, Path] = {}
    
    def download_file_from_url(self, url: str, filename: str) -> Optional[Path]:
        """
        Download a file from Google Drive using gdown
        
        Args:
            url: Google Drive sharing URL
            filename: Name to save the file as
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            file_path = self.cache_dir / filename
            
            # Check if file already exists
            if file_path.exists():
                logging.info(f"File already exists: {filename}")
                self.downloaded_files[filename] = file_path
                return file_path
            
            logging.info(f"Downloading {filename} from Google Drive...")
            
            # Download using gdown
            output_path = gdown.download(url, str(file_path), quiet=False, fuzzy=True)
            
            if output_path and Path(output_path).exists():
                self.downloaded_files[filename] = Path(output_path)
                logging.info(f"Successfully downloaded: {filename}")
                return Path(output_path)
            else:
                logging.error(f"Failed to download {filename}")
                return None
                
        except Exception as e:
            logging.error(f"Error downloading {filename}: {e}")
            return None
    
    def download_file_from_id(self, file_id: str, filename: str) -> Optional[Path]:
        """
        Download a file from Google Drive using file ID
        
        Args:
            file_id: Google Drive file ID
            filename: Name to save the file as
            
        Returns:
            Path to downloaded file or None if failed
        """
        url = f"https://drive.google.com/uc?id={file_id}"
        return self.download_file_from_url(url, filename)
    
    def get_cached_file(self, filename: str) -> Optional[Path]:
        """
        Get cached file if it exists
        
        Args:
            filename: Name of the file
            
        Returns:
            Path to cached file or None if not found
        """
        file_path = self.cache_dir / filename
        if file_path.exists():
            logging.info(f"Using cached file: {filename}")
            self.downloaded_files[filename] = file_path
            return file_path
        return None
    
    def clear_cache(self):
        """Clear all cached files"""
        for file in self.cache_dir.glob("*"):
            if file.is_file():
                file.unlink()
        self.downloaded_files.clear()
        logging.info("Cache cleared")
    
    def get_downloaded_files(self) -> Dict[str, Path]:
        """Get all downloaded file paths"""
        return self.downloaded_files.copy()
    
    def verify_file_exists(self, filename: str) -> bool:
        """Verify if a file exists in cache"""
        file_path = self.cache_dir / filename
        return file_path.exists() 