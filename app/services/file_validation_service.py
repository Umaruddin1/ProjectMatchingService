"""File validation service."""
import logging
from pathlib import Path
from app.core.config import settings
from app.core.exceptions import FileValidationException

logger = logging.getLogger(__name__)


class FileValidationService:
    """Validates uploaded files."""
    
    @staticmethod
    def validate_file(file_path: str) -> bool:
        """
        Validate that file exists and is Excel format.
        
        Args:
            file_path: Path to file
            
        Returns:
            bool: True if valid
            
        Raises:
            FileValidationException: If validation fails
        """
        logger.info(f"Validating file: {file_path}")
        
        path = Path(file_path)
        
        # Check file exists
        if not path.exists():
            raise FileValidationException(f"File not found: {file_path}")
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise FileValidationException(
                f"File too large: {file_size} bytes (max {settings.MAX_UPLOAD_SIZE})"
            )
        
        # Check file extension
        suffix = path.suffix.lower()
        if suffix not in settings.ALLOWED_EXTENSIONS:
            raise FileValidationException(
                f"Invalid file type: {suffix}. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
        
        logger.info(f"File validation passed: {file_path}")
        return True
