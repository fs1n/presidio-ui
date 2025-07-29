import os
import shutil
import logging
from typing import List
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class FileService:
    """Service for handling file uploads and management"""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.results_dir = Path(settings.results_dir)
        
        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"File service initialized: upload_dir={self.upload_dir}, results_dir={self.results_dir}")
    
    async def save_upload_file(self, upload_file: UploadFile) -> Path:
        """Save uploaded file to upload directory"""
        try:
            # Validate file size
            if upload_file.size and upload_file.size > settings.max_file_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {settings.max_file_size} bytes"
                )
            
            # Create unique filename
            file_path = self.upload_dir / upload_file.filename
            counter = 1
            original_stem = file_path.stem
            
            while file_path.exists():
                file_path = self.upload_dir / f"{original_stem}_{counter}{file_path.suffix}"
                counter += 1
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save upload file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save file")
    
    async def read_file(self, file_path: Path) -> bytes:
        """Read file content as bytes"""
        try:
            with open(file_path, "rb") as file:
                return file.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to read file")
    
    async def save_result_file(self, content: bytes, filename: str) -> Path:
        """Save result content to results directory"""
        try:
            file_path = self.results_dir / filename
            
            with open(file_path, "wb") as file:
                file.write(content)
            
            logger.info(f"Result file saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save result file: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save result file")
    
    async def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old files from upload and results directories"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for directory in [self.upload_dir, self.results_dir]:
                for file_path in directory.iterdir():
                    if file_path.is_file():
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > max_age_seconds:
                            file_path.unlink()
                            logger.info(f"Cleaned up old file: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old files: {str(e)}")
    
    def get_supported_file_types(self) -> List[str]:
        """Get list of supported file types"""
        return [".pdf", ".txt", ".png", ".jpg", ".jpeg"]
    
    def validate_file_type(self, filename: str) -> bool:
        """Validate if file type is supported"""
        file_extension = Path(filename).suffix.lower()
        return file_extension in self.get_supported_file_types()
