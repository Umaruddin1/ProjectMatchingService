"""Application configuration."""
import os


class Settings:
    """Application settings."""
    
    PROJECT_NAME = "Accounting Reconciliation Service"
    API_VERSION = "v1"
    
    # File upload config
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB - supports large Excel files with 1500+ rows
    ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}  # Added .xlsm support
    
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
        "summary sheet",
        "summary",
    }
    
    # Previous year sheet names (variations to handle)
    PREVIOUS_YEAR_SHEET_NAMES = {
        "previous year",
        "previous_year",
        "previous-year",
        "py",
        "year 0",
        "year0",
        "ref_summary_sheet",
        "ref_summary sheet",
        "reference summary",
    }
    
    # Required headers - will be normalized and matched
    CURRENT_YEAR_REQUIRED_HEADERS = {
        "project name",
        "additions",
        "transfer",
        "closing balance",  # Can be "as on 31 mar", "as on 31 mar 25", etc.
    }
    
    PREVIOUS_YEAR_REQUIRED_HEADERS = {
        "project name",
        "opening balance",  # Can include year variations like "opening balance 20/21"
        "additions",
        "transfer",
        "closing balance",
    }


settings = Settings()
