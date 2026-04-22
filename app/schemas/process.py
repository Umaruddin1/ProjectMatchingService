"""Process endpoint schemas."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ParsedRow(BaseModel):
    """A parsed row from Excel."""
    row_number: int
    project_name: str
    values: Dict[str, float]  # All numeric values normalized


class Match(BaseModel):
    """A match between current year and previous year rows."""
    current_row_number: int
    previous_row_number: int
    project_name: str
    match_type: str  # "exact" or "fuzzy"
    confidence: Optional[float] = None


class SuggestedMatch(BaseModel):
    """A suggested fuzzy match."""
    current_row_number: int
    current_project_name: str
    suggested_previous_row_number: Optional[int] = None
    suggested_project_name: Optional[str] = None
    confidence: float


class ProcessResponse(BaseModel):
    """Response from /api/v1/process endpoint."""
    success: bool
    
    # Parsed data
    current_year_rows: List[ParsedRow] = []
    previous_year_rows: List[ParsedRow] = []
    
    # Matching results
    exact_matches: List[Match] = []
    suggested_matches: List[SuggestedMatch] = []
    unmatched_current_rows: List[ParsedRow] = []
    unmatched_previous_rows: List[ParsedRow] = []
    
    # Validation
    validation_issues: List[Dict[str, Any]] = []
    
    # Impact preview (for matched rows)
    impact_preview: List[Dict[str, Any]] = []
    
    # Summary
    summary: Dict[str, Any] = {}
    
    error: Optional[str] = None
    details: Optional[str] = None
