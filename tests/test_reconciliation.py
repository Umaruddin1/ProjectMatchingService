"""Tests for reconciliation service."""
import pytest
from app.services.reconciliation_service import ReconciliationService


class TestReconciliation:
    """Test reconciliation calculations."""
    
    def test_wip_impact_positive(self):
        """Test WIP impact calculation with positive change."""
        wip = ReconciliationService.calculate_wip_impact(100.0, 50.0)
        assert wip == 50.0
    
    def test_wip_impact_negative(self):
        """Test WIP impact calculation with negative change."""
        wip = ReconciliationService.calculate_wip_impact(50.0, 100.0)
        assert wip == -50.0
    
    def test_wip_impact_zero(self):
        """Test WIP impact calculation with no change."""
        wip = ReconciliationService.calculate_wip_impact(100.0, 100.0)
        assert wip == 0.0
    
    def test_far_impact_positive(self):
        """Test FAR impact calculation with positive change."""
        far = ReconciliationService.calculate_far_impact(200.0, 100.0)
        assert far == 100.0
    
    def test_far_impact_negative(self):
        """Test FAR impact calculation with negative change."""
        far = ReconciliationService.calculate_far_impact(50.0, 150.0)
        assert far == -100.0
    
    def test_far_impact_zero(self):
        """Test FAR impact calculation with no change."""
        far = ReconciliationService.calculate_far_impact(100.0, 100.0)
        assert far == 0.0
    
    def test_calculate_impacts_for_match(self):
        """Test calculating both impacts for a match."""
        current = {
            "opening_balance": 100.0,
            "additions": 50.0,
            "transfer": 25.0,
            "closing_balance": 125.0,
        }
        previous = {
            "opening_balance": 80.0,
            "additions": 40.0,
            "transfer": 20.0,
            "closing_balance": 100.0,
        }
        
        impacts = ReconciliationService.calculate_impacts_for_match(current, previous)
        
        assert impacts["wip_impact"] == 10.0  # 50 - 40 (additions diff)
        assert impacts["far_impact"] == 5.0   # 25 - 20
    
    def test_reconcile_matches(self):
        """Test reconciling multiple matches."""
        matches = [
            {
                "current_idx": 0,
                "previous_idx": 0,
            },
        ]
        
        current_rows = [
            {
                "row_number": 2,
                "project_name": "Project A",
                "values": {
                    "opening_balance": 100.0,
                    "additions": 50.0,
                    "transfer": 25.0,
                    "closing_balance": 125.0,
                },
            },
        ]
        
        previous_rows = [
            {
                "row_number": 2,
                "project_name": "Project A",
                "values": {
                    "opening_balance": 80.0,
                    "additions": 40.0,
                    "transfer": 20.0,
                    "closing_balance": 100.0,
                },
            },
        ]
        
        reconciled = ReconciliationService.reconcile_matches(
            matches, current_rows, previous_rows
        )
        
        assert len(reconciled) == 1
        assert reconciled[0]["wip_impact"] == 10.0
        assert reconciled[0]["far_impact"] == 5.0
    
    def test_calculate_summary(self):
        """Test calculating summary statistics."""
        reconciled = [
            {"wip_impact": 100.0, "far_impact": 50.0},
            {"wip_impact": 200.0, "far_impact": -25.0},
        ]
        
        summary = ReconciliationService.calculate_summary(
            reconciled, all_current_rows=5, all_previous_rows=5
        )
        
        assert summary["total_matched"] == 2
        assert summary["total_unmatched_current"] == 3
        assert summary["total_unmatched_previous"] == 3
        assert summary["total_wip_impact"] == 300.0
        assert summary["total_far_impact"] == 25.0
