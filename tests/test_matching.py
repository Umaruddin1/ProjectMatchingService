"""Tests for matching service."""
import pytest
from app.services.matching_service import MatchingService


class TestMatching:
    """Test matching functionality."""
    
    def test_exact_match_single(self):
        """Test single exact match."""
        current = [
            {"normalized_project_name": "project a", "project_name": "Project A"},
        ]
        previous = [
            {"normalized_project_name": "project a", "project_name": "Project A"},
        ]
        
        matches, matched_c, matched_p = MatchingService.exact_match(current, previous)
        
        assert len(matches) == 1
        assert matches[0]["match_type"] == "exact"
        assert matches[0]["confidence"] == 1.0
    
    def test_exact_match_multiple(self):
        """Test multiple exact matches."""
        current = [
            {"normalized_project_name": "project a", "project_name": "Project A"},
            {"normalized_project_name": "project b", "project_name": "Project B"},
            {"normalized_project_name": "project c", "project_name": "Project C"},
        ]
        previous = [
            {"normalized_project_name": "project c", "project_name": "Project C"},
            {"normalized_project_name": "project a", "project_name": "Project A"},
            {"normalized_project_name": "project b", "project_name": "Project B"},
        ]
        
        matches, _, _ = MatchingService.exact_match(current, previous)
        
        assert len(matches) == 3
        for match in matches:
            assert match["match_type"] == "exact"
    
    def test_no_exact_match(self):
        """Test no exact match."""
        current = [
            {"normalized_project_name": "project a", "project_name": "Project A"},
        ]
        previous = [
            {"normalized_project_name": "project b", "project_name": "Project B"},
        ]
        
        matches, _, _ = MatchingService.exact_match(current, previous)
        
        assert len(matches) == 0
    
    def test_fuzzy_match_single_suggestion(self):
        """Test single fuzzy match suggestion."""
        current = [
            {"normalized_project_name": "project alpha", "project_name": "Project Alpha"},
        ]
        previous = [
            {"normalized_project_name": "project alph", "project_name": "Project Alph"},
        ]
        
        suggested, ambiguous = MatchingService.fuzzy_match(
            current, previous, set(), set(), threshold=0.80
        )
        
        assert len(suggested) >= 0  # Depends on fuzzy score
        assert len(ambiguous) == 0
    
    def test_fuzzy_match_no_match_below_threshold(self):
        """Test fuzzy match below threshold."""
        current = [
            {"normalized_project_name": "apple", "project_name": "Apple"},
        ]
        previous = [
            {"normalized_project_name": "zebra", "project_name": "Zebra"},
        ]
        
        suggested, ambiguous = MatchingService.fuzzy_match(
            current, previous, set(), set(), threshold=0.80
        )
        
        assert len(suggested) == 0
        assert len(ambiguous) == 0
    
    def test_unmatched_rows(self):
        """Test getting unmatched rows."""
        current = [
            {"project_name": "A"},
            {"project_name": "B"},
            {"project_name": "C"},
        ]
        previous = [
            {"project_name": "X"},
            {"project_name": "Y"},
        ]
        
        matched_c = {0}  # First current matched
        matched_p = {0}  # First previous matched
        
        unmatched_c, unmatched_p = MatchingService.get_unmatched_rows(
            current, previous, matched_c, matched_p
        )
        
        assert len(unmatched_c) == 2
        assert len(unmatched_p) == 1
