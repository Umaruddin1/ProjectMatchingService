"""Normalization service."""
import logging
from typing import Dict, List, Any
from app.utils.text_normalizer import normalize_text
from app.utils.number_parser import safe_parse_number, parse_number
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class NormalizationService:
    """Normalizes and validates data."""
    
    @staticmethod
    def normalize_project_name(name: Any) -> str:
        """
        Normalize a project name for matching.
        
        Args:
            name: Raw project name
            
        Returns:
            str: Normalized name
        """
        if not name:
            return ""
        return normalize_text(str(name))
    
    @staticmethod
    def normalize_row_data(
        row: Dict[str, Any],
        header_mapping: Dict[str, str],
        sheet_type: str
    ) -> Dict[str, Any]:
        """
        Normalize a single row of data.
        
        Args:
            row: Raw row dict
            header_mapping: Mapping of normalized header -> original header
            sheet_type: "current_year" or "previous_year"
            
        Returns:
            Dict with normalized data and validation issues
        """
        result = {
            "project_name": "",
            "values": {},
            "validation_issues": []
        }
        
        # Extract and normalize project name
        project_name_original = row.get(header_mapping.get("project name"))
        if not project_name_original:
            result["validation_issues"].append(
                "Project name is empty or missing"
            )
            return result
        
        result["project_name"] = NormalizationService.normalize_project_name(
            project_name_original
        )
        
        # Define fields to extract based on sheet type
        if sheet_type == "current_year":
            field_keys = {
                "as of 31 mar": "opening_balance",
                "additions": "additions",
                "transfer": "transfer",
                "as on 31 mar": "closing_balance",
            }
        else:  # previous_year
            field_keys = {
                "opening balance": "opening_balance",
                "additions": "additions",
                "transfer": "transfer",
                "closing balance": "closing_balance",
            }
        
        # Extract and parse numeric values
        for normalized_key, output_key in field_keys.items():
            original_key = header_mapping.get(normalized_key)
            if original_key:
                raw_value = row.get(original_key)
                try:
                    parsed_value = safe_parse_number(raw_value)
                    result["values"][output_key] = parsed_value
                except Exception as e:
                    result["validation_issues"].append(
                        f"Error parsing {normalized_key}: {e}"
                    )
        
        return result
    
    @staticmethod
    def validate_formulas(
        row_values: Dict[str, float],
        sheet_type: str
    ) -> Dict[str, Any]:
        """
        Validate accounting formulas for a row.
        
        Current year: opening + additions - transfer = closing
        Previous year: opening + additions - transfer = closing
        
        Args:
            row_values: Parsed row values
            sheet_type: "current_year" or "previous_year"
            
        Returns:
            Dict with validation result
        """
        result = {
            "valid": True,
            "issues": []
        }
        
        opening = row_values.get("opening_balance", 0.0)
        additions = row_values.get("additions", 0.0)
        transfer = row_values.get("transfer", 0.0)
        closing = row_values.get("closing_balance", 0.0)
        
        # Calculate expected closing
        expected_closing = opening + additions - transfer
        
        # Allow small floating point tolerance
        tolerance = 0.01
        if abs(expected_closing - closing) > tolerance:
            result["valid"] = False
            result["issues"].append(
                f"Formula mismatch: {opening} + {additions} - {transfer} = "
                f"{expected_closing}, but got {closing}"
            )
        
        return result
