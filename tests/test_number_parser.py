"""Tests for number parsing utilities."""
import pytest
from app.utils.number_parser import parse_number, safe_parse_number


class TestNumberParser:
    """Test number parsing functionality."""
    
    def test_parse_integer(self):
        """Test parsing integer."""
        assert parse_number(100) == 100.0
        assert parse_number("100") == 100.0
    
    def test_parse_float(self):
        """Test parsing float."""
        assert parse_number(10.5) == 10.5
        assert parse_number("10.5") == 10.5
    
    def test_parse_with_commas(self):
        """Test parsing number with commas."""
        assert parse_number("1,000.00") == 1000.0
        assert parse_number("1,000,000.50") == 1000000.5
    
    def test_parse_with_whitespace(self):
        """Test parsing with surrounding whitespace."""
        assert parse_number("  100  ") == 100.0
        assert parse_number("\t50.5\n") == 50.5
    
    def test_parse_dash(self):
        """Test parsing dash as zero."""
        assert parse_number("-") == 0.0
    
    def test_parse_empty_string(self):
        """Test parsing empty string."""
        assert parse_number("") == 0.0
        assert parse_number(None) == 0.0
    
    def test_parse_negative_number(self):
        """Test parsing negative number."""
        assert parse_number("-100") == -100.0
        # Accounting format (-50) is not standard float, so we skip it
        with pytest.raises(ValueError):
            parse_number("(-50)")
    
    def test_parse_invalid(self):
        """Test parsing invalid value."""
        with pytest.raises(ValueError):
            parse_number("abc")
        
        with pytest.raises(ValueError):
            parse_number("10x20")
    
    def test_safe_parse_number(self):
        """Test safe parsing with default."""
        assert safe_parse_number("100") == 100.0
        assert safe_parse_number("invalid") == 0.0
        assert safe_parse_number("invalid", default=999.0) == 999.0
