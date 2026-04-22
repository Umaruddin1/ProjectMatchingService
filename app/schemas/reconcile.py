"""Reconcile endpoint schemas."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ApprovedMatch(BaseModel):
    """User-approved mapping."""
    current_row_number: int
    previous_row_number: Optional[int] = None  # None means unmatched
    match_type: str = "approved"


class ReconcileRequest(BaseModel):
    """Request for reconciliation endpoint."""
    approved_matches: List[ApprovedMatch]
    manual_overrides: Optional[Dict[int, int]] = None  # current_row -> previous_row


class ReconcileResult(BaseModel):
    """A reconciled/matched row with impacts."""
    current_row_number: int
    previous_row_number: Optional[int] = None
    project_name: str
    current_values: Dict[str, float]
    previous_values: Optional[Dict[str, float]] = None
    wip_impact: Optional[float] = None
    far_impact: Optional[float] = None


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
    
    # Totals
    total_wip_impact: float = 0.0
    total_far_impact: float = 0.0
    
    error: Optional[str] = None
    details: Optional[str] = None
