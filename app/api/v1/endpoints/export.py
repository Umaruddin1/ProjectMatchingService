"""Export endpoint."""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.core.exceptions import ExportException
from app.services.export_service import ExportService
from app.schemas.export import ExportRequest, ExportResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/export")
async def export(request: ExportRequest) -> FileResponse:
    """
    Generate and download Excel export.
    
    - Accept final reconciled payload
    - Generate Excel file
    - Return file for download
    """
    logger.info("Export requested")
    
    try:
        # Create export workbook
        file_path = ExportService.create_export_workbook(
            reconciled_matches=request.reconciled_matches,
            unmatched_current_rows=request.unmatched_current_rows,
            unmatched_previous_rows=request.unmatched_previous_rows,
            validation_issues=request.validation_issues,
            summary=request.summary,
        )
        
        logger.info(f"Export file created: {file_path}")
        
        # Return file
        return FileResponse(
            path=file_path,
            filename=file_path.split("\\")[-1],
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    except ExportException as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during export: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
