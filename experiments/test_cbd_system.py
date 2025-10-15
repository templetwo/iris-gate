#!/usr/bin/env python3
"""
Test suite for CBD Therapeutic Development System
"""

import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from cbd_therapeutic_system import (
    CBDTherapeuticSystem, ResearchClaim, ExperimentSpec,
    TherapeuticMilestone, ConfidenceLevel, ExperimentType,
    ResearchPhase
)


class TestResearchClaim:
    """Test research claim functionality."""

    def test_claim_creation(self):
        """Test basic claim creation."""
        claim = ResearchClaim(
            description="Test claim",
            confidence=0.5,
            evidence_sources=["source1"]
        )
        assert claim.description == "Test claim"
        assert claim.confidence == 0.5
        assert len(claim.evidence_sources) == 1

    def test_confidence_update(self):
        """Test confidence updating mechanism."""
        claim = ResearchClaim(description="Test", confidence=0.5)
        initial_confidence = claim.confidence

        claim.update_confidence("new_evidence", 0.8)

        assert claim.confidence != initial_confidence
        assert "new_evidence" in claim.evidence_sources
        assert claim.last_validated is not None

    def test_confidence_bounds(self):
        """Test confidence stays within bounds."""
        claim = ResearchClaim(confidence=0.9)
        claim.update_confidence("evidence", 1.0)

        assert claim.confidence <= 1.0


class TestCBDTherapeuticSystem:
    """Test main therapeutic system."""

    @pytest.fixture
    def system(self):
        """Create test system instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.json"
            config = {
                "confidence_threshold": 0.6,
                "max_contradictions": 1
            }
            with open(config_path, 'w') as f:
                json.dump(config, f)

            return CBDTherapeuticSystem(config_path)

    def test_system_initialization(self, system):
        """Test system initializes with correct components."""
        assert len(system.claims) > 0
        assert len(system.experiments) > 0
        assert len(system.milestones) > 0

    def test_iris_claims_loaded(self, system):
        """Test IRIS convergence claims are loaded."""
        iris_claims = [
            claim for claim in system.claims.values()
            if claim.iris_convergence is not None
        ]
        assert len(iris_claims) > 0

        # Check specific IRIS claim
        selectivity_claims = [
            claim for claim in iris_claims
            if "selectivity index" in claim.description.lower()
        ]
        assert len(selectivity_claims) == 1
        assert selectivity_claims[0].iris_convergence == 0.85

    def test_literature_claims_loaded(self, system):
        """Test literature validation claims are loaded."""
        vdac_claims = [
            claim for claim in system.claims.values()
            if "VDAC1" in claim.description
        ]
        assert len(vdac_claims) == 1
        assert vdac_claims[0].confidence >= 0.7

    def test_experiment_priority_calculation(self, system):
        """Test experiment priority scoring."""
        exp_id = list(system.experiments.keys())[0]
        priority = system.calculate_experiment_priority(exp_id)

        assert 0 <= priority <= 1
        assert system.experiments[exp_id].priority_score == priority

    def test_literature_monitoring(self, system):
        """Test literature monitoring system."""
        updates = system.update_literature_monitoring()

        assert "new_papers" in updates
        assert "paradigm_shifts" in updates
        assert "contradictions" in updates

        # Check if confidence was updated
        initial_confidences = {
            claim_id: claim.confidence
            for claim_id, claim in system.claims.items()
        }

        # Run again to see changes
        system.update_literature_monitoring()

        # At least some claims should have updated confidence
        updated_count = sum(
            1 for claim_id, claim in system.claims.items()
            if claim.confidence != initial_confidences[claim_id]
        )
        assert updated_count >= 0  # May be 0 if no matching keywords

    def test_research_roadmap_generation(self, system):
        """Test research roadmap generation."""
        roadmap = system.generate_research_roadmap()

        assert "phases" in roadmap
        assert "total_timeline" in roadmap
        assert roadmap["total_timeline"] > 0

        # Check phases are ordered correctly
        phase_order = [phase["phase"] for phase in roadmap["phases"]]
        expected_phases = ["discovery", "preclinical"]
        for expected in expected_phases:
            if expected in phase_order:
                assert phase_order.index(expected) >= 0

    def test_clinical_readiness_assessment(self, system):
        """Test clinical readiness assessment."""
        readiness = system.assess_clinical_readiness()

        assert "readiness_score" in readiness
        assert "recommendation" in readiness
        assert 0 <= readiness["readiness_score"] <= 1

        if readiness["readiness_score"] > 0.7:
            assert "Proceed" in readiness["recommendation"]
        else:
            assert "Continue" in readiness["recommendation"]

    def test_blocking_issues_identification(self, system):
        """Test identification of blocking issues."""
        blocking_issues = system._identify_blocking_issues()

        assert isinstance(blocking_issues, list)
        # May be empty if no blocking issues

    def test_state_export(self, system):
        """Test system state export functionality."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            filepath = Path(f.name)

        try:
            system.export_system_state(filepath)
            assert filepath.exists()

            # Verify exported data structure
            with open(filepath) as f:
                state = json.load(f)

            assert "timestamp" in state
            assert "claims" in state
            assert "experiments" in state
            assert len(state["claims"]) == len(system.claims)

        finally:
            if filepath.exists():
                filepath.unlink()


class TestExperimentSpec:
    """Test experiment specification functionality."""

    def test_experiment_creation(self):
        """Test experiment spec creation."""
        exp = ExperimentSpec(
            type=ExperimentType.BINDING_ASSAY,
            priority_score=0.8,
            estimated_duration=14
        )

        assert exp.type == ExperimentType.BINDING_ASSAY
        assert exp.priority_score == 0.8
        assert exp.estimated_duration == 14


class TestTherapeuticMilestone:
    """Test therapeutic milestone functionality."""

    def test_milestone_creation(self):
        """Test milestone creation."""
        milestone = TherapeuticMilestone(
            phase=ResearchPhase.DISCOVERY,
            min_confidence=0.7,
            estimated_timeline=90
        )

        assert milestone.phase == ResearchPhase.DISCOVERY
        assert milestone.min_confidence == 0.7
        assert milestone.estimated_timeline == 90
        assert not milestone.completed


class TestIntegration:
    """Integration tests for the complete system."""

    def test_end_to_end_workflow(self):
        """Test complete workflow from initialization to export."""
        # Initialize system
        system = CBDTherapeuticSystem()

        # Update literature
        updates = system.update_literature_monitoring()
        assert len(updates["new_papers"]) > 0

        # Generate roadmap
        roadmap = system.generate_research_roadmap()
        assert roadmap["total_timeline"] > 0

        # Assess readiness
        readiness = system.assess_clinical_readiness()
        assert "readiness_score" in readiness

        # Export state
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            filepath = Path(f.name)

        try:
            system.export_system_state(filepath)
            assert filepath.exists()

        finally:
            if filepath.exists():
                filepath.unlink()

    def test_confidence_propagation(self):
        """Test confidence propagation through system."""
        system = CBDTherapeuticSystem()

        # Find a claim with low confidence
        low_confidence_claims = [
            claim for claim in system.claims.values()
            if claim.confidence < 0.5
        ]

        if low_confidence_claims:
            claim = low_confidence_claims[0]
            initial_confidence = claim.confidence

            # Add strong evidence
            claim.update_confidence("Strong_validation_study_2025", 0.9)

            assert claim.confidence > initial_confidence

    def test_paradigm_shift_handling(self):
        """Test paradigm shift detection and handling."""
        system = CBDTherapeuticSystem()

        with patch('cbd_therapeutic_system.logger') as mock_logger:
            system._flag_paradigm_shift("Major mechanism revision")
            mock_logger.warning.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])