"""Text normalization utilities."""
import re
import unicodedata


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.
    
    - Lowercase
    - Strip whitespace
    - Remove extra spaces
    - Remove accents
    - Keep alphanumeric and spaces only
    
    Args:
        text: Text to normalize
        
    Returns:
        str: Normalized text
    """
    if not text:
        return ""
    
    # Convert to string
    text = str(text).strip()
    
    # Lowercase
    text = text.lower()
    
    # Remove accents
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode("ASCII")
    
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    
    # Keep only alphanumeric and spaces
    text = re.sub(r"[^a-z0-9\s]", "", text)
    
    # Strip again
    text = text.strip()
    
    return text


def normalize_header(header: str) -> str:
    """
    Normalize a column header for matching.
    
    Args:
        header: Column header text
        
    Returns:
        str: Normalized header
    """
    return normalize_text(header)
