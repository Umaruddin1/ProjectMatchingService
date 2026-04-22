"""Application configuration."""
import os


class Settings:
    """Application settings."""
    
    PROJECT_NAME = "Accounting Reconciliation Service"
    API_VERSION = "v1"
    
    # File upload config
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
    
    # Matching config
    FUZZY_MATCH_THRESHOLD = 0.80
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Current year sheet names (variations to handle)
    CURRENT_YEAR_SHEET_NAMES = {
        "current year",
        "current_year",
        "current-year",
        "cy",
        "year 1",
        "year1",
    }
    
    # Previous year sheet names (variations to handle)
    PREVIOUS_YEAR_SHEET_NAMES = {
        "previous year",
        "previous_year",
        "previous-year",
        "py",
        "year 0",
        "year0",
    }
    
    # Required headers - will be normalized and matched
    CURRENT_YEAR_REQUIRED_HEADERS = {
        "project name",
        "as of 31 mar",
        "additions",
        "transfer",
        "as on 31 mar",
    }
    
    PREVIOUS_YEAR_REQUIRED_HEADERS = {
        "project name",
        "opening balance",
        "additions",
        "transfer",
        "closing balance",
    }


settings = Settings()
