"""Reconciliation service."""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ReconciliationService:
    """Calculates reconciliation impacts."""
    
    @staticmethod
    def calculate_wip_impact(
        current_closing: float,
        previous_closing: float
    ) -> float:
        """
        Calculate WIP Impact.
        
        WIP Impact = Current Year Closing Balance - Previous Year Closing Balance
        
        Args:
            current_closing: Current year "As on 31 Mar" value
            previous_closing: Previous year "Closing Balance" value
            
        Returns:
            float: WIP Impact
        """
        return current_closing - previous_closing
    
    @staticmethod
    def calculate_far_impact(
        current_transfer: float,
        previous_transfer: float
    ) -> float:
        """
        Calculate FAR Impact.
        
        FAR Impact = Current Year Transfer - Previous Year Transfer
        
        Args:
            current_transfer: Current year "Transfer" value
            previous_transfer: Previous year "Transfer" value
            
        Returns:
            float: FAR Impact
        """
        return current_transfer - previous_transfer
    
    @staticmethod
    def calculate_impacts_for_match(
        current_values: Dict[str, float],
        previous_values: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate WIP and FAR impacts for a matched row.
        
        Args:
            current_values: Parsed current year values
            previous_values: Parsed previous year values
            
        Returns:
            Dict with wip_impact and far_impact
        """
        current_closing = current_values.get("closing_balance", 0.0)
        previous_closing = previous_values.get("closing_balance", 0.0)
        
        current_transfer = current_values.get("transfer", 0.0)
        previous_transfer = previous_values.get("transfer", 0.0)
        
        wip_impact = ReconciliationService.calculate_wip_impact(
            current_closing, previous_closing
        )
        far_impact = ReconciliationService.calculate_far_impact(
            current_transfer, previous_transfer
        )
        
        return {
            "wip_impact": wip_impact,
            "far_impact": far_impact,
        }

    @staticmethod
    def zero_values() -> Dict[str, float]:
        """Return zeroed numeric values for unmatched rows."""
        return {
            "opening_balance": 0.0,
            "additions": 0.0,
            "transfer": 0.0,
            "closing_balance": 0.0,
        }
    
    @staticmethod
    def reconcile_matches(
        matches: List[Dict[str, Any]],
        current_rows: List[Dict[str, Any]],
        previous_rows: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Reconcile all matched rows and calculate impacts.
        
        Args:
            matches: List of approved matches
            current_rows: All current year rows
            previous_rows: All previous year rows
            
        Returns:
            List of reconciled matches with impacts
        """
        reconciled = []
        
        for match in matches:
            current_idx = match.get("current_idx")
            previous_idx = match.get("previous_idx")
            
            if current_idx is None or previous_idx is None:
                continue
            
            current_row = current_rows[current_idx]
            previous_row = previous_rows[previous_idx]
            
            impacts = ReconciliationService.calculate_impacts_for_match(
                current_row.get("values", {}),
                previous_row.get("values", {})
            )
            
            reconciled.append({
                "current_row_number": current_row.get("row_number"),
                "current_project": current_row.get("project_name"),
                "previous_row_number": previous_row.get("row_number"),
                "previous_project": previous_row.get("project_name"),
                "current_values": current_row.get("values", {}),
                "previous_values": previous_row.get("values", {}),
                "wip_impact": impacts["wip_impact"],
                "far_impact": impacts["far_impact"],
            })
        
        logger.info(f"Reconciled {len(reconciled)} matches")
        return reconciled
    
    @staticmethod
    def calculate_summary(
        reconciled_matches: List[Dict[str, Any]],
        all_current_rows: int,
        all_previous_rows: int
    ) -> Dict[str, Any]:
        """
        Calculate summary statistics.
        
        Args:
            reconciled_matches: List of reconciled matches
            all_current_rows: Total current year rows
            all_previous_rows: Total previous year rows
            
        Returns:
            Dict with summary statistics
        """
        total_wip = sum(m.get("wip_impact", 0.0) for m in reconciled_matches)
        total_far = sum(m.get("far_impact", 0.0) for m in reconciled_matches)

        total_matched = sum(1 for m in reconciled_matches if m.get("match_status") == "matched")
        total_unmatched_current = sum(1 for m in reconciled_matches if m.get("match_status") == "unmatched_current")
        total_unmatched_previous = sum(1 for m in reconciled_matches if m.get("match_status") == "unmatched_previous")
        
        return {
            "total_current_rows": all_current_rows,
            "total_previous_rows": all_previous_rows,
            "total_matched": total_matched,
            "total_unmatched_current": total_unmatched_current,
            "total_unmatched_previous": total_unmatched_previous,
            "total_wip_impact": total_wip,
            "total_far_impact": total_far,
        }
