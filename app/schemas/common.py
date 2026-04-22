"""Common response schemas."""
from pydantic import BaseModel
from typing import Optional, Dict, Any


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = True
    data: Dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    details: Optional[str] = None


class ValidationIssue(BaseModel):
    """A data validation issue."""
    row_number: int
    project_name: Optional[str] = None
    issue_type: str  # "missing_header", "formula_mismatch", "parse_error", etc.
    description: str
    values: Optional[Dict[str, Any]] = None
