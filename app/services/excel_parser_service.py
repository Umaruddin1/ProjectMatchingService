"""Excel parser service."""
import logging
from typing import Tuple, List, Dict, Any
from app.utils.excel_helpers import load_excel_workbook, get_sheet_names, read_sheet_data
from app.utils.text_normalizer import normalize_text, normalize_header
from app.utils.number_parser import safe_parse_number, parse_number
from app.core.config import settings
from app.core.exceptions import ParsingException, ValidationException

logger = logging.getLogger(__name__)


class ExcelParserService:
    """Parses Excel workbook data."""
    
    @staticmethod
    def find_sheet_by_keywords(sheet_names: List[str], keywords: set) -> str:
        """
        Find a sheet name matching keywords (case-insensitive).
        
        Args:
            sheet_names: List of available sheet names
            keywords: Set of keyword variations
            
        Returns:
            str: Matching sheet name
            
        Raises:
            ParsingException: If no sheet found
        """
        normalized_keywords = {normalize_header(kw) for kw in keywords}
        
        for sheet_name in sheet_names:
            if normalize_header(sheet_name) in normalized_keywords:
                return sheet_name
        
        raise ParsingException(
            f"Could not find sheet. Looking for: {keywords}. "
            f"Found: {sheet_names}"
        )
    
    @staticmethod
    def parse_single_sheet(file_path: str) -> Tuple[List[Dict], List[str]]:
        """
        Parse a single Excel file (assumes one sheet with data).
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Tuple of (rows, headers)
            
        Raises:
            ParsingException: If parsing fails
        """
        logger.info(f"Parsing single sheet from: {file_path}")
        
        try:
            workbook = load_excel_workbook(file_path)
            sheet_names = get_sheet_names(workbook)
            
            if not sheet_names:
                raise ParsingException("No sheets found in workbook")
            
            # Use first sheet
            sheet_name = sheet_names[0]
            logger.info(f"Using sheet: {sheet_name}")
            
            sheet = workbook[sheet_name]
            rows, headers = read_sheet_data(sheet)
            
            logger.info(f"Parsed {len(rows)} rows with {len(headers)} headers")
            
            return rows, headers
            
        except ParsingException:
            raise
        except Exception as e:
            logger.error(f"Failed to parse file: {e}")
            raise ParsingException(f"Failed to parse file: {e}") from e
    
    @staticmethod
    def parse_workbook(file_path: str) -> Tuple[List[Dict], List[Dict], List[str], List[str]]:
        """
        Parse workbook and extract current year and previous year data.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Tuple of (current_year_rows, previous_year_rows, current_headers, previous_headers)
            
        Raises:
            ParsingException: If parsing fails
        """
        logger.info(f"Parsing workbook: {file_path}")
        
        try:
            workbook = load_excel_workbook(file_path)
            sheet_names = get_sheet_names(workbook)
            logger.info(f"Found sheets: {sheet_names}")
            
            # Find current year sheet
            current_year_sheet_name = ExcelParserService.find_sheet_by_keywords(
                sheet_names, settings.CURRENT_YEAR_SHEET_NAMES
            )
            logger.info(f"Found current year sheet: {current_year_sheet_name}")
            
            # Find previous year sheet
            previous_year_sheet_name = ExcelParserService.find_sheet_by_keywords(
                sheet_names, settings.PREVIOUS_YEAR_SHEET_NAMES
            )
            logger.info(f"Found previous year sheet: {previous_year_sheet_name}")
            
            # Read sheets
            current_sheet = workbook[current_year_sheet_name]
            previous_sheet = workbook[previous_year_sheet_name]
            
            current_rows, current_headers = read_sheet_data(current_sheet)
            previous_rows, previous_headers = read_sheet_data(previous_sheet)
            
            logger.info(f"Current year: {len(current_rows)} rows, {len(current_headers)} cols")
            logger.info(f"Previous year: {len(previous_rows)} rows, {len(previous_headers)} cols")
            
            return current_rows, previous_rows, current_headers, previous_headers
            
        except ParsingException:
            raise
        except Exception as e:
            logger.error(f"Failed to parse workbook: {e}")
            raise ParsingException(f"Failed to parse workbook: {e}") from e
    
    @staticmethod
    def normalize_headers(headers: List[str]) -> Dict[str, str]:
        """
        Map raw headers to normalized headers.
        
        Args:
            headers: Raw header names
            
        Returns:
            Dict mapping normalized header -> original header
        """
        mapping = {}
        for header in headers:
            if header:
                normalized = normalize_header(header)
                mapping[normalized] = header
        return mapping
    
    @staticmethod
    def validate_and_extract_headers(
        headers: List[str],
        required_fields: set,
        sheet_type: str
    ) -> Tuple[Dict[str, str], List[str]]:
        """
        Validate headers and extract mapping to required fields.
        
        Args:
            headers: Raw headers from sheet
            required_fields: Set of required field names (normalized)
            sheet_type: "current_year" or "previous_year"
            
        Returns:
            Tuple of (header_mapping, validation_issues)
            
        Raises:
            ValidationException: If required headers missing
        """
        normalized = ExcelParserService.normalize_headers(headers)
        validation_issues = []
        
        missing_headers = required_fields - set(normalized.keys())
        if missing_headers:
            msg = f"Missing required headers in {sheet_type}: {missing_headers}"
            logger.error(msg)
            raise ValidationException(msg)
        
        return normalized, validation_issues
