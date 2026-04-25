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

        def zero_current_values() -> Dict[str, Any]:
            return {
                "opening_balance": 0,
                "additions": 0,
                "transfer": 0,
                "closing_balance": 0,
            }

        def zero_previous_values() -> Dict[str, Any]:
            return {
                "opening_balance": 0,
                "additions": 0,
                "transfer": 0,
                "closing_balance": 0,
            }
        
        reconciled_matches: List[ReconcileResult] = []
        total_wip = 0.0
        total_far = 0.0
        matched_current_rows = set()
        matched_previous_rows = set()
        
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
            
            current_values = current_row.values or zero_current_values()
            previous_values = previous_row.values if previous_row else zero_previous_values()

            impacts = ReconciliationService.calculate_impacts_for_match(
                current_values,
                previous_values,
            )
            wip_impact = impacts.get("wip_impact", 0.0)
            far_impact = impacts.get("far_impact", 0.0)

            matched_current_rows.add(current_row_num)
            if previous_row_num:
                matched_previous_rows.add(previous_row_num)
            
            reconciled_matches.append(
                ReconcileResult(
                    current_row_number=current_row_num,
                    previous_row_number=previous_row_num,
                    project_name=current_row.project_name,
                    current_project=current_row.project_name,
                    previous_project=previous_row.project_name if previous_row else None,
                    current_values=current_row.values,
                    previous_values=previous_row.values if previous_row else None,
                    wip_impact=wip_impact,
                    far_impact=far_impact,
                    match_status="matched",
                    requires_review=False,
                    match_type=approved_match.match_type or "matched",
                )
            )
            total_wip += wip_impact
            total_far += far_impact

        unmatched_current_rows = []
        unmatched_previous_rows = []

        if request.include_unmatched_rows:
            # Add any current year rows that were not matched at all.
            for current_row_num, current_row in current_rows.items():
                if current_row_num in matched_current_rows:
                    continue

                impacts = ReconciliationService.calculate_impacts_for_match(
                    current_row.values or zero_current_values(),
                    zero_previous_values(),
                )

                reconciled_matches.append(
                    ReconcileResult(
                        current_row_number=current_row_num,
                        previous_row_number=None,
                        project_name=current_row.project_name,
                        current_project=current_row.project_name,
                        previous_project=None,
                        current_values=current_row.values,
                        previous_values=zero_previous_values(),
                        wip_impact=impacts.get("wip_impact", 0.0),
                        far_impact=impacts.get("far_impact", 0.0),
                        match_status="unmatched_current",
                        requires_review=True,
                        match_type=None,
                    )
                )
                total_wip += impacts.get("wip_impact", 0.0)
                total_far += impacts.get("far_impact", 0.0)

            # Add any previous year rows that were not matched at all.
            for previous_row_num, previous_row in previous_rows.items():
                if previous_row_num in matched_previous_rows:
                    continue

                impacts = ReconciliationService.calculate_impacts_for_match(
                    zero_current_values(),
                    previous_row.values or zero_previous_values(),
                )

                reconciled_matches.append(
                    ReconcileResult(
                        current_row_number=None,
                        previous_row_number=previous_row_num,
                        project_name=previous_row.project_name,
                        current_project=None,
                        previous_project=previous_row.project_name,
                        current_values=zero_current_values(),
                        previous_values=previous_row.values,
                        wip_impact=impacts.get("wip_impact", 0.0),
                        far_impact=impacts.get("far_impact", 0.0),
                        match_status="unmatched_previous",
                        requires_review=True,
                        match_type=None,
                    )
                )
                total_wip += impacts.get("wip_impact", 0.0)
                total_far += impacts.get("far_impact", 0.0)

            unmatched_current_rows = [
                row for row in request.current_year_rows if row.row_number not in matched_current_rows
            ]
            unmatched_previous_rows = [
                row for row in request.previous_year_rows if row.row_number not in matched_previous_rows
            ]
        
        response = ReconcileResponse(
            success=True,
            reconciled_matches=reconciled_matches,
            unmatched_current_rows=[row.model_dump() if hasattr(row, "model_dump") else row.dict() for row in unmatched_current_rows],
            unmatched_previous_rows=[row.model_dump() if hasattr(row, "model_dump") else row.dict() for row in unmatched_previous_rows],
            total_current_rows=len(request.current_year_rows),
            total_previous_rows=len(request.previous_year_rows),
            total_matched=len(matched_current_rows),
            total_unmatched=len(unmatched_current_rows) + len(unmatched_previous_rows),
            total_unmatched_current=len(unmatched_current_rows),
            total_unmatched_previous=len(unmatched_previous_rows),
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
