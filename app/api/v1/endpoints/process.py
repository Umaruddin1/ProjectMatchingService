"""Process endpoint."""
import logging
import tempfile
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.exceptions import ProcessingException, FileValidationException, ParsingException, ValidationException
from app.services.file_validation_service import FileValidationService
from app.services.excel_parser_service import ExcelParserService
from app.services.normalization_service import NormalizationService
from app.services.matching_service import MatchingService
from app.services.reconciliation_service import ReconciliationService
from app.schemas.process import ProcessResponse, ParsedRow

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/process", response_model=ProcessResponse)
async def process_file(
    current_year_file: UploadFile = File(...),
    previous_year_file: UploadFile = File(...)
) -> ProcessResponse:
    """
    Process two uploaded Excel files.
    
    - Parse current year file
    - Parse previous year file
    - Validate headers and data in both
    - Normalize project names
    - Perform exact and fuzzy matching between files
    - Calculate impact preview
    - Return JSON preview
    """
    logger.info(f"Received uploads: {current_year_file.filename} and {previous_year_file.filename}")
    
    try:
        # Save both uploaded files temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_cy:
            content = await current_year_file.read()
            tmp_cy.write(content)
            current_year_path = tmp_cy.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_py:
            content = await previous_year_file.read()
            tmp_py.write(content)
            previous_year_path = tmp_py.name
        
        # Validate files
        FileValidationService.validate_file(current_year_path)
        FileValidationService.validate_file(previous_year_path)
        
        # Parse files (each file is a single sheet, not workbook with multiple sheets)
        logger.info("Parsing current year file")
        current_raw, current_headers = ExcelParserService.parse_single_sheet(current_year_path)
        
        logger.info("Parsing previous year file")
        previous_raw, previous_headers = ExcelParserService.parse_single_sheet(previous_year_path)
        
        # Validate and map headers
        logger.info("Validating headers")
        from app.core.config import settings
        
        current_header_map, _ = ExcelParserService.validate_and_extract_headers(
            current_headers,
            settings.CURRENT_YEAR_REQUIRED_HEADERS,
            "current_year"
        )
        
        previous_header_map, _ = ExcelParserService.validate_and_extract_headers(
            previous_headers,
            settings.PREVIOUS_YEAR_REQUIRED_HEADERS,
            "previous_year"
        )
        
        # Normalize and validate data
        logger.info("Normalizing and validating data")
        current_rows = []
        current_validation_issues = []
        
        for idx, raw_row in enumerate(current_raw, start=2):
            normalized = NormalizationService.normalize_row_data(
                raw_row, current_header_map, "current_year"
            )
            
            if normalized["validation_issues"]:
                current_validation_issues.append({
                    "row_number": idx,
                    "project_name": normalized["project_name"],
                    "issue_type": "data_validation",
                    "file_type": "current_year",
                    "file_name": current_year_file.filename,
                    "sheet": "Current Year",
                    "source_label": "Current Year Sheet",
                    "description": "; ".join(normalized["validation_issues"]),
                })
            
            # Validate formulas
            formula_validation = NormalizationService.validate_formulas(
                normalized["values"], "current_year"
            )
            
            if not formula_validation["valid"]:
                current_validation_issues.append({
                    "row_number": idx,
                    "project_name": normalized["project_name"],
                    "issue_type": "formula_mismatch",
                    "file_type": "current_year",
                    "file_name": current_year_file.filename,
                    "sheet": "Current Year",
                    "source_label": "Current Year Sheet",
                    "description": formula_validation["issues"][0],
                })
            
            current_rows.append({
                "row_number": idx,
                "project_name": normalized["project_name"],
                "normalized_project_name": NormalizationService.normalize_project_name(
                    normalized["project_name"]
                ),
                "values": normalized["values"],
            })
        
        previous_rows = []
        previous_validation_issues = []
        
        for idx, raw_row in enumerate(previous_raw, start=2):
            normalized = NormalizationService.normalize_row_data(
                raw_row, previous_header_map, "previous_year"
            )
            
            if normalized["validation_issues"]:
                previous_validation_issues.append({
                    "row_number": idx,
                    "project_name": normalized["project_name"],
                    "issue_type": "data_validation",
                    "file_type": "previous_year",
                    "file_name": previous_year_file.filename,
                    "sheet": "Previous Year",
                    "source_label": "Previous Year Sheet",
                    "description": "; ".join(normalized["validation_issues"]),
                })
            
            # Validate formulas
            formula_validation = NormalizationService.validate_formulas(
                normalized["values"], "previous_year"
            )
            
            if not formula_validation["valid"]:
                previous_validation_issues.append({
                    "row_number": idx,
                    "project_name": normalized["project_name"],
                    "issue_type": "formula_mismatch",
                    "file_type": "previous_year",
                    "file_name": previous_year_file.filename,
                    "sheet": "Previous Year",
                    "source_label": "Previous Year Sheet",
                    "description": formula_validation["issues"][0],
                })
            
            previous_rows.append({
                "row_number": idx,
                "project_name": normalized["project_name"],
                "normalized_project_name": NormalizationService.normalize_project_name(
                    normalized["project_name"]
                ),
                "values": normalized["values"],
            })
        
        logger.info(f"Parsed {len(current_rows)} current year rows, "
                   f"{len(previous_rows)} previous year rows")
        
        # Perform matching
        logger.info("Performing matching")
        exact_matches, matched_current, matched_previous = MatchingService.exact_match(
            current_rows, previous_rows
        )
        
        suggested_matches, ambiguous_matches = MatchingService.fuzzy_match(
            current_rows, previous_rows, matched_current, matched_previous
        )
        
        unmatched_current, unmatched_previous = MatchingService.get_unmatched_rows(
            current_rows, previous_rows, matched_current, matched_previous
        )
        
        # Convert matches to proper format for response
        formatted_exact_matches = []
        for match in exact_matches:
            formatted_exact_matches.append({
                "current_row_number": current_rows[match["current_idx"]]["row_number"],
                "previous_row_number": previous_rows[match["previous_idx"]]["row_number"],
                "project_name": match["current_project"],
                "match_type": "exact",
                "confidence": 1.0,
            })
        
        formatted_suggested_matches = []
        for match in suggested_matches:
            formatted_suggested_matches.append({
                "current_row_number": current_rows[match["current_idx"]]["row_number"],
                "current_project_name": current_rows[match["current_idx"]]["project_name"],
                "suggested_previous_row_number": previous_rows[match["previous_idx"]]["row_number"],
                "suggested_project_name": match["previous_project"],
                "confidence": match["confidence"],
            })

        formatted_ambiguous_matches = []
        for match in ambiguous_matches:
            formatted_ambiguous_matches.append({
                "current_row_number": current_rows[match["current_idx"]]["row_number"],
                "current_project_name": current_rows[match["current_idx"]]["project_name"],
                "match_status": "ambiguous_match",
                "requires_review": True,
                "candidates": [
                    {
                        "previous_row_number": previous_rows[candidate["idx"]]["row_number"],
                        "previous_project_name": candidate.get("project"),
                        "confidence": candidate.get("score"),
                    }
                    for candidate in match.get("candidates", [])
                ],
            })
        
        # Calculate impact preview for exact matches
        impact_preview = []
        for match in exact_matches:
            current_row = current_rows[match["current_idx"]]
            previous_row = previous_rows[match["previous_idx"]]
            
            impacts = ReconciliationService.calculate_impacts_for_match(
                current_row["values"],
                previous_row["values"]
            )
            
            impact_preview.append({
                "current_row_number": current_row["row_number"],
                "previous_row_number": previous_row["row_number"],
                "project_name": match["current_project"],
                "wip_impact": impacts["wip_impact"],
                "far_impact": impacts["far_impact"],
            })
        all_validation_issues = current_validation_issues + previous_validation_issues
        
        # Build summary
        summary = {
            "total_current_rows": len(current_rows),
            "total_previous_rows": len(previous_rows),
            "exact_matches": len(exact_matches),
            "suggested_fuzzy_matches": len(suggested_matches),
            "ambiguous_fuzzy_matches": len(ambiguous_matches),
            "unmatched_current": len(unmatched_current),
            "unmatched_previous": len(unmatched_previous),
            "validation_issues": len(all_validation_issues),
        }
        
        logger.info(f"Processing complete. Summary: {summary}")
        
        return ProcessResponse(
            success=True,
            current_year_rows=[
                ParsedRow(row_number=r["row_number"], 
                         project_name=r["project_name"],
                         values=r["values"])
                for r in current_rows
            ],
            previous_year_rows=[
                ParsedRow(row_number=r["row_number"],
                         project_name=r["project_name"],
                         values=r["values"])
                for r in previous_rows
            ],
            exact_matches=formatted_exact_matches,
            suggested_matches=formatted_suggested_matches,
            ambiguous_matches=formatted_ambiguous_matches,
            unmatched_current_rows=[
                ParsedRow(row_number=r["row_number"],
                         project_name=r["project_name"],
                         values=r["values"])
                for r in unmatched_current
            ],
            unmatched_previous_rows=[
                ParsedRow(row_number=r["row_number"],
                         project_name=r["project_name"],
                         values=r["values"])
                for r in unmatched_previous
            ],
            validation_issues=all_validation_issues,
            impact_preview=impact_preview,
            summary=summary,
        )
    
    except FileValidationException as e:
        logger.error(f"File validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ParsingException as e:
        logger.error(f"Parsing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ValidationException as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
