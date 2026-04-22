"""Reconcile endpoint."""
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from app.core.exceptions import ProcessingException
from app.services.reconciliation_service import ReconciliationService
from app.schemas.reconcile import ReconcileRequest, ReconcileResponse, ReconcileResult

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store for process results (normally would be session-based or database)
_process_results = {}


def store_process_result(session_id: str, result: Dict[str, Any]):
    """Store process result for later reconciliation."""
    _process_results[session_id] = result


def get_process_result(session_id: str) -> Dict[str, Any]:
    """Retrieve stored process result."""
    return _process_results.get(session_id)


@router.post("/reconcile", response_model=ReconcileResponse)
async def reconcile(
    request: ReconcileRequest,
    session_id: str = None  # Would be from cookie/header in production
) -> ReconcileResponse:
    """
    Reconcile and finalize matches.
    
    - Accept approved/manual mappings from frontend
    - Recalculate final impacts
    - Return final reconciled JSON
    """
    logger.info(f"Reconciliation requested with {len(request.approved_matches)} matches")
    
    try:
        # In production, would retrieve from session/database
        # For now, we'll build matches from the request
        
        # Convert approved matches to internal format
        internal_matches = []
        for approved in request.approved_matches:
            internal_matches.append({
                "current_idx": approved.current_row_number - 2,  # Adjust for 0-indexing and header
                "previous_idx": approved.previous_row_number - 2 if approved.previous_row_number else None,
            })
        
        # Apply manual overrides if provided
        if request.manual_overrides:
            for current_row, previous_row in request.manual_overrides.items():
                internal_matches.append({
                    "current_idx": current_row - 2,
                    "previous_idx": previous_row - 2,
                })
        
        # In a real scenario, we'd have actual row data from the process step
        # For now, return a valid response structure
        
        reconciled_matches: List[ReconcileResult] = []
        total_wip = 0.0
        total_far = 0.0
        
        for match in internal_matches:
            if match.get("previous_idx") is not None:
                # Calculate impacts (using dummy data for now)
                wip = 0.0
                far = 0.0
                
                reconciled_matches.append(
                    ReconcileResult(
                        current_row_number=match["current_idx"] + 2,
                        previous_row_number=match["previous_idx"] + 2 if match["previous_idx"] else None,
                        project_name="Project",
                        current_values={},
                        previous_values={},
                        wip_impact=wip,
                        far_impact=far,
                    )
                )
                total_wip += wip
                total_far += far
        
        response = ReconcileResponse(
            success=True,
            reconciled_matches=reconciled_matches,
            total_matched=len([m for m in internal_matches if m.get("previous_idx") is not None]),
            total_unmatched_current=len([m for m in internal_matches if m.get("previous_idx") is None]),
            total_wip_impact=total_wip,
            total_far_impact=total_far,
        )
        
        logger.info(f"Reconciliation complete. Matched: {response.total_matched}, "
                   f"WIP Impact: {total_wip}, FAR Impact: {total_far}")
        
        return response
    
    except ProcessingException as e:
        logger.error(f"Processing error during reconciliation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during reconciliation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
