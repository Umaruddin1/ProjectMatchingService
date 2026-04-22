"""Matching service."""
import logging
from typing import List, Dict, Tuple, Optional
from fuzzywuzzy import fuzz
from app.core.config import settings

logger = logging.getLogger(__name__)


class MatchingService:
    """Performs exact and fuzzy matching."""
    
    @staticmethod
    def exact_match(
        current_rows: List[Dict],
        previous_rows: List[Dict]
    ) -> Tuple[List[Dict], List[int], List[int]]:
        """
        Find exact matches between current and previous year rows.
        
        Args:
            current_rows: List of current year rows with normalized data
            previous_rows: List of previous year rows with normalized data
            
        Returns:
            Tuple of (matches, matched_current_indices, matched_previous_indices)
        """
        logger.info("Performing exact matching")
        
        matches = []
        matched_current = set()
        matched_previous = set()
        
        for c_idx, current_row in enumerate(current_rows):
            current_name = current_row.get("normalized_project_name", "")
            if not current_name:
                continue
            
            for p_idx, previous_row in enumerate(previous_rows):
                if p_idx in matched_previous:
                    continue
                
                previous_name = previous_row.get("normalized_project_name", "")
                if not previous_name:
                    continue
                
                if current_name == previous_name:
                    matches.append({
                        "current_idx": c_idx,
                        "previous_idx": p_idx,
                        "match_type": "exact",
                        "confidence": 1.0,
                        "current_project": current_row.get("project_name"),
                        "previous_project": previous_row.get("project_name"),
                    })
                    matched_current.add(c_idx)
                    matched_previous.add(p_idx)
                    logger.debug(f"Exact match: '{current_name}'")
                    break
        
        logger.info(f"Found {len(matches)} exact matches")
        return matches, matched_current, matched_previous
    
    @staticmethod
    def fuzzy_match(
        current_rows: List[Dict],
        previous_rows: List[Dict],
        matched_current: set,
        matched_previous: set,
        threshold: float = settings.FUZZY_MATCH_THRESHOLD
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Find fuzzy matches for unmatched rows.
        
        Returns:
        - suggested matches (one best match per unmatched current row)
        - ambiguous matches (current rows with multiple similar matches)
        
        Args:
            current_rows: List of current year rows with normalized data
            previous_rows: List of previous year rows with normalized data
            matched_current: Set of already matched current indices
            matched_previous: Set of already matched previous indices
            threshold: Fuzzy match confidence threshold (0-1)
            
        Returns:
            Tuple of (suggested_matches, ambiguous_matches)
        """
        logger.info(f"Performing fuzzy matching (threshold: {threshold})")
        
        suggested_matches = []
        ambiguous_matches = []
        
        for c_idx, current_row in enumerate(current_rows):
            if c_idx in matched_current:
                continue
            
            current_name = current_row.get("normalized_project_name", "")
            if not current_name:
                continue
            
            # Find all candidates above threshold
            candidates = []
            for p_idx, previous_row in enumerate(previous_rows):
                if p_idx in matched_previous:
                    continue
                
                previous_name = previous_row.get("normalized_project_name", "")
                if not previous_name:
                    continue
                
                # Use token_set_ratio for better fuzzy matching
                score = fuzz.token_set_ratio(current_name, previous_name) / 100.0
                
                if score >= threshold:
                    candidates.append({
                        "idx": p_idx,
                        "score": score,
                        "project": previous_row.get("project_name"),
                        "normalized": previous_name,
                    })
            
            # Sort by score descending
            candidates.sort(key=lambda x: x["score"], reverse=True)
            
            if len(candidates) == 0:
                # No fuzzy matches
                pass
            elif len(candidates) == 1:
                # One clear suggestion
                best = candidates[0]
                suggested_matches.append({
                    "current_idx": c_idx,
                    "previous_idx": best["idx"],
                    "match_type": "fuzzy_suggested",
                    "confidence": best["score"],
                    "current_project": current_row.get("project_name"),
                    "previous_project": best["project"],
                })
                logger.debug(
                    f"Fuzzy match (confidence {best['score']:.2%}): "
                    f"'{current_name}' -> '{best['normalized']}'"
                )
            else:
                # Multiple candidates - ambiguous
                ambiguous_matches.append({
                    "current_idx": c_idx,
                    "current_project": current_row.get("project_name"),
                    "current_normalized": current_name,
                    "candidates": candidates,
                })
                logger.debug(
                    f"Ambiguous fuzzy match for '{current_name}': "
                    f"{len(candidates)} candidates"
                )
        
        logger.info(
            f"Found {len(suggested_matches)} fuzzy suggestions, "
            f"{len(ambiguous_matches)} ambiguous"
        )
        return suggested_matches, ambiguous_matches
    
    @staticmethod
    def get_unmatched_rows(
        current_rows: List[Dict],
        previous_rows: List[Dict],
        matched_current: set,
        matched_previous: set
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Get lists of unmatched rows.
        
        Args:
            current_rows: All current year rows
            previous_rows: All previous year rows
            matched_current: Indices of matched current rows
            matched_previous: Indices of matched previous rows
            
        Returns:
            Tuple of (unmatched_current, unmatched_previous)
        """
        unmatched_current = [
            row for idx, row in enumerate(current_rows)
            if idx not in matched_current
        ]
        
        unmatched_previous = [
            row for idx, row in enumerate(previous_rows)
            if idx not in matched_previous
        ]
        
        logger.info(
            f"Unmatched: {len(unmatched_current)} current, "
            f"{len(unmatched_previous)} previous"
        )
        
        return unmatched_current, unmatched_previous
