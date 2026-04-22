"""Export endpoint schemas."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ExportRequest(BaseModel):
    """Request for export endpoint."""
    reconciled_matches: List[Dict[str, Any]] = []
    unmatched_current_rows: List[Dict[str, Any]] = []
    unmatched_previous_rows: List[Dict[str, Any]] = []
    validation_issues: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {}


class ExportResponse(BaseModel):
    """Response from /api/v1/export endpoint."""
    success: bool
    
    # File info
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    
    error: Optional[str] = None
    details: Optional[str] = None
