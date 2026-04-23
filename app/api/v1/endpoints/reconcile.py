"""Reconcile endpoint."""
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body
from app.core.exceptions import ProcessingException
from app.services.reconciliation_service import ReconciliationService
from app.schemas.reconcile import ReconcileRequest, ReconcileResponse, ReconcileResult

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/reconcile", response_model=ReconcileResponse)
async def reconcile(request: ReconcileRequest) -> ReconcileResponse:
    """
    Reconcile and finalize matches.
    
    Expected request body:
    {
      "current_year_rows": [...],
      "previous_year_rows": [...],
      "approved_matches": [
        {
          "current_row_number": 2,
          "previous_row_number": 2,
          "match_type": "exact"
        }
      ],
      "manual_overrides": {}
    }
    
    - Accept approved/manual mappings from frontend (from /process response)
    - Recalculate final impacts using actual row data
    - Return final reconciled JSON
    """
    logger.info(f"Reconciliation requested with {len(request.approved_matches)} approved matches")
    
    try:
        # Extract row data from request
        current_rows = {row.row_number: row for row in request.current_year_rows}
        previous_rows = {row.row_number: row for row in request.previous_year_rows}
        
        reconciled_matches: List[ReconcileResult] = []
        total_wip = 0.0
        total_far = 0.0
        
        # Process approved matches
        for approved_match in request.approved_matches:
            current_row_num = approved_match.current_row_number
            previous_row_num = approved_match.previous_row_number
            
            # Get row data
            current_row = current_rows.get(current_row_num)
            previous_row = previous_rows.get(previous_row_num) if previous_row_num else None
            
            if not current_row:
                logger.warning(f"Current row {current_row_num} not found")
                continue
            
            if previous_row_num and not previous_row:
                logger.warning(f"Previous row {previous_row_num} not found")
                continue
            
            # Calculate impacts
            wip_impact = 0.0
            far_impact = 0.0
            
            if previous_row:
                impacts = ReconciliationService.calculate_impacts_for_match(
                    current_row.values,
                    previous_row.values
                )
                wip_impact = impacts.get("wip_impact", 0.0)
                far_impact = impacts.get("far_impact", 0.0)
            
            reconciled_matches.append(
                ReconcileResult(
                    current_row_number=current_row_num,
                    previous_row_number=previous_row_num,
                    project_name=current_row.project_name,
                    current_values=current_row.values,
                    previous_values=previous_row.values if previous_row else None,
                    wip_impact=wip_impact,
                    far_impact=far_impact,
                )
            )
            total_wip += wip_impact
            total_far += far_impact
        
        response = ReconcileResponse(
            success=True,
            reconciled_matches=reconciled_matches,
            total_matched=len([m for m in reconciled_matches if m.previous_row_number]),
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
