"""Export endpoint."""
import logging
from io import BytesIO
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.core.exceptions import ExportException
from app.core.security import get_current_username
from app.services.export_service import ExportService
from app.schemas.export import ExportRequest

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(get_current_username)])


@router.post("/export")
async def export(request: ExportRequest) -> StreamingResponse:
    """
    Generate and download Excel export.
    
    - Accept final reconciled payload
    - Generate Excel file
    - Return file for download
    """
    logger.info("Export requested")
    
    try:
        # Create export workbook in memory
        file_bytes, file_name = ExportService.create_export_workbook(
            reconciled_matches=request.reconciled_matches,
            unmatched_current_rows=request.unmatched_current_rows,
            unmatched_previous_rows=request.unmatched_previous_rows,
            validation_issues=request.validation_issues,
            summary=request.summary,
        )
        
        logger.info("Export file created in memory: %s", file_name)

        return StreamingResponse(
            BytesIO(file_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
        )
    
    except ExportException as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during export: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
