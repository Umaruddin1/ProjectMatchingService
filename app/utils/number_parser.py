"""Number parsing utilities."""
import re


def parse_number(value) -> float:
    """
    Parse a numeric value from a cell.
    
    Handles:
    - None / empty strings -> 0
    - "-" -> 0
    - Numbers with commas
    - Whitespace trimming
    
    Args:
        value: Raw cell value
        
    Returns:
        float: Parsed number
        
    Raises:
        ValueError: If value cannot be parsed
    """
    if value is None or value == "":
        return 0.0
    
    # Convert to string and strip whitespace
    str_value = str(value).strip()
    
    if str_value == "-":
        return 0.0
    
    if str_value == "":
        return 0.0
    
    # Remove commas
    str_value = str_value.replace(",", "")
    
    try:
        return float(str_value)
    except ValueError as e:
        raise ValueError(f"Cannot parse '{str_value}' as number") from e


def safe_parse_number(value, default=0.0) -> float:
    """
    Safely parse a number, returning default on error.
    
    Args:
        value: Raw cell value
        default: Default value if parsing fails
        
    Returns:
        float: Parsed number or default
    """
    try:
        return parse_number(value)
    except ValueError:
        return default
