"""Tests for text normalization utilities."""
import pytest
from app.utils.text_normalizer import normalize_text, normalize_header


class TestTextNormalizer:
    """Test text normalization functionality."""
    
    def test_normalize_lowercase(self):
        """Test normalization to lowercase."""
        assert normalize_text("HELLO") == "hello"
        assert normalize_text("HeLLo") == "hello"
    
    def test_normalize_whitespace(self):
        """Test normalization of whitespace."""
        assert normalize_text("  hello  ") == "hello"
        assert normalize_text("hello   world") == "hello world"
        assert normalize_text("\thello\nworld\t") == "hello world"
    
    def test_normalize_special_chars(self):
        """Test removal of special characters."""
        assert normalize_text("hello@world") == "helloworld"
        assert normalize_text("hello-world") == "helloworld"
        assert normalize_text("hello_world") == "helloworld"
    
    def test_normalize_accents(self):
        """Test removal of accents."""
        assert normalize_text("café") == "cafe"
        assert normalize_text("naïve") == "naive"
    
    def test_normalize_empty(self):
        """Test normalization of empty/none."""
        assert normalize_text("") == ""
        assert normalize_text(None) == ""
    
    def test_normalize_header(self):
        """Test header normalization."""
        assert normalize_header("Project Name") == "project name"
        assert normalize_header("As of 31 Mar") == "as of 31 mar"
        assert normalize_header("Opening Balance") == "opening balance"
    
    def test_normalize_complex(self):
        """Test complex normalization."""
        text = "  Project-Name (Copy) #123  "
        normalized = normalize_text(text)
        # The dash is removed, so it becomes "projectname copy 123"
        assert normalized == "projectname copy 123"
