"""Reconcile endpoint schemas."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ApprovedMatch(BaseModel):
    """User-approved mapping."""
    current_row_number: int
    previous_row_number: Optional[int] = None  # None means unmatched
    match_type: str = "approved"


class ParsedRowForReconcile(BaseModel):
    """Row data for reconciliation."""
    row_number: int
    project_name: str
    values: Dict[str, Any]


class ReconcileRequest(BaseModel):
    """Request for reconciliation endpoint."""
    current_year_rows: List[ParsedRowForReconcile]
    previous_year_rows: List[ParsedRowForReconcile]
    approved_matches: List[ApprovedMatch]
    manual_overrides: Optional[Dict[int, int]] = None  # current_row -> previous_row
    include_unmatched_rows: bool = True


class ReconcileResult(BaseModel):
    """A reconciled/matched row with impacts."""
    current_row_number: Optional[int] = None
    previous_row_number: Optional[int] = None
    project_name: str
    current_project: Optional[str] = None  # Alias for export
    previous_project: Optional[str] = None  # For export when different
    current_values: Dict[str, Any]
    previous_values: Optional[Dict[str, Any]] = None
    wip_impact: Optional[float] = None
    far_impact: Optional[float] = None
    match_status: str = "matched"
    requires_review: bool = False
    match_type: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Set current_project if not explicitly set
        if not self.current_project:
            self.current_project = self.project_name
        # Set previous_project if not explicitly set
        if not self.previous_project and self.previous_row_number:
            self.previous_project = self.project_name


class ReconcileResponse(BaseModel):
    """Response from /api/v1/reconcile endpoint."""
    success: bool
    
    # Reconciled matches
    reconciled_matches: List[ReconcileResult] = []
    unmatched_current_rows: List[Dict[str, Any]] = []
    unmatched_previous_rows: List[Dict[str, Any]] = []
    
    # Summary
    total_current_rows: int = 0
    total_previous_rows: int = 0
    total_matched: int = 0
    total_unmatched: int = 0
    total_unmatched_current: int = 0
    total_unmatched_previous: int = 0
    
    # Totals
    total_wip_impact: float = 0.0
    total_far_impact: float = 0.0
    
    error: Optional[str] = None
    details: Optional[str] = None
