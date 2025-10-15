#!/usr/bin/env python3
"""
CBD Therapeutic Development System
Synthesizes IRIS convergence data with literature validation for therapeutic pipeline.

Architecture Overview:
- Research Knowledge Graph: Tracks claims, evidence, and confidence
- Literature Monitoring: Automated updates and paradigm shift detection
- Experimental Pipeline: Maps IRIS insights to wet-lab validation
- Therapeutic Roadmap: Clinical development pathway with decision points
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
import hashlib
import re


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence levels for research claims."""
    EXPERIMENTAL = 0.3  # IRIS phenomenology only
    PRELIMINARY = 0.5   # Single literature source
    SUPPORTED = 0.7     # Multiple convergent sources
    VALIDATED = 0.9     # Experimental confirmation
    CLINICAL = 1.0      # Clinical trial validation


class ExperimentType(Enum):
    """Types of validation experiments."""
    BINDING_ASSAY = "binding_assay"
    CELL_VIABILITY = "cell_viability"
    SELECTIVITY = "selectivity_index"
    BIOMARKER = "biomarker_validation"
    MECHANISM = "mechanism_confirmation"
    DOSING = "dosing_optimization"


class ResearchPhase(Enum):
    """Therapeutic development phases."""
    DISCOVERY = "discovery"
    PRECLINICAL = "preclinical"
    PHASE_I = "phase_1"
    PHASE_II = "phase_2"
    PHASE_III = "phase_3"
    REGULATORY = "regulatory"


@dataclass
class ResearchClaim:
    """Individual research claim with evidence tracking."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    confidence: float = 0.0
    evidence_sources: List[str] = field(default_factory=list)
    iris_convergence: Optional[float] = None
    last_validated: Optional[datetime] = None
    dependencies: Set[str] = field(default_factory=set)
    contradictions: List[str] = field(default_factory=list)

    def update_confidence(self, new_evidence: str, evidence_weight: float) -> None:
        """Update confidence based on new evidence."""
        self.evidence_sources.append(new_evidence)
        # Weighted average with diminishing returns
        current_weight = len(self.evidence_sources) - 1
        self.confidence = (self.confidence * current_weight + evidence_weight) / len(self.evidence_sources)
        self.confidence = min(self.confidence, 1.0)
        self.last_validated = datetime.now()


@dataclass
class ExperimentSpec:
    """Specification for validation experiment."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: ExperimentType = ExperimentType.BINDING_ASSAY
    target_claims: List[str] = field(default_factory=list)
    protocol: Dict = field(default_factory=dict)
    expected_outcomes: Dict = field(default_factory=dict)
    priority_score: float = 0.0
    estimated_duration: int = 30  # days
    resource_requirements: Dict = field(default_factory=dict)
    success_criteria: Dict = field(default_factory=dict)


@dataclass
class TherapeuticMilestone:
    """Development milestone with go/no-go criteria."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    phase: ResearchPhase = ResearchPhase.DISCOVERY
    required_claims: List[str] = field(default_factory=list)
    min_confidence: float = 0.7
    experiments: List[str] = field(default_factory=list)
    decision_criteria: Dict = field(default_factory=dict)
    estimated_timeline: int = 90  # days
    completed: bool = False


class CBDTherapeuticSystem:
    """Main system for CBD therapeutic development pipeline."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the therapeutic development system."""
        self.config = self._load_config(config_path)
        self.claims: Dict[str, ResearchClaim] = {}
        self.experiments: Dict[str, ExperimentSpec] = {}
        self.milestones: Dict[str, TherapeuticMilestone] = {}
        self.literature_cache: Dict[str, Dict] = {}
        self._initialize_iris_claims()
        self._initialize_literature_claims()
        self._setup_development_pipeline()

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load system configuration."""
        default_config = {
            "literature_update_interval": 7,  # days
            "confidence_threshold": 0.6,
            "max_contradictions": 2,
            "priority_weights": {
                "therapeutic_impact": 0.4,
                "feasibility": 0.3,
                "cost": 0.2,
                "timeline": 0.1
            }
        }

        if config_path and config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                default_config.update(config)

        return default_config

    def _initialize_iris_claims(self) -> None:
        """Initialize research claims from IRIS convergence data."""
        iris_claims = [
            {
                "description": "CBD selectivity index 1.53 (corrected from 2.86 claim)",
                "confidence": 0.6,
                "iris_convergence": 0.85,
                "evidence_sources": ["IRIS_S8_document", "CBD_v2_session"]
            },
            {
                "description": "Rhythm patterns 0.5-2.0 Hz indicate pulse dosing potential",
                "confidence": 0.4,
                "iris_convergence": 0.78,
                "evidence_sources": ["IRIS_S4_patterns"]
            },
            {
                "description": "Center stability 0.7-0.98 suggests therapeutic window",
                "confidence": 0.5,
                "iris_convergence": 0.82,
                "evidence_sources": ["IRIS_S4_patterns"]
            },
            {
                "description": "Aperture range 0.3-0.9 correlates with dosing flexibility",
                "confidence": 0.3,
                "iris_convergence": 0.75,
                "evidence_sources": ["IRIS_S4_patterns"]
            }
        ]

        for claim_data in iris_claims:
            claim = ResearchClaim(**claim_data)
            self.claims[claim.id] = claim
            logger.info(f"Initialized IRIS claim: {claim.description[:50]}...")

    def _initialize_literature_claims(self) -> None:
        """Initialize claims from literature validation."""
        literature_claims = [
            {
                "description": "VDAC1 direct binding validated with therapeutic KD range",
                "confidence": 0.8,
                "evidence_sources": ["Literature_2024_VDAC1", "Multiple_binding_studies"]
            },
            {
                "description": "ROS-dependent selectivity mechanism confirmed",
                "confidence": 0.7,
                "evidence_sources": ["Literature_2024_ROS", "Oxidative_stress_studies"]
            },
            {
                "description": "TRPV4 emerging as biomarker for CBD response",
                "confidence": 0.6,
                "evidence_sources": ["Literature_2025_TRPV4", "Biomarker_studies"]
            },
            {
                "description": "MCU-CBD interaction gap requires investigation",
                "confidence": 0.3,
                "evidence_sources": ["Literature_gap_analysis"]
            },
            {
                "description": "Chloride channel mechanisms remain unclear",
                "confidence": 0.2,
                "evidence_sources": ["Literature_review_2025"]
            },
            {
                "description": "Channel-first mechanism superior to receptor-first approach",
                "confidence": 0.7,
                "evidence_sources": ["Mechanism_comparison_2024", "IRIS_convergence"]
            }
        ]

        for claim_data in literature_claims:
            claim = ResearchClaim(**claim_data)
            self.claims[claim.id] = claim
            logger.info(f"Initialized literature claim: {claim.description[:50]}...")

    def _setup_development_pipeline(self) -> None:
        """Setup therapeutic development milestones and experiments."""
        self._create_validation_experiments()
        self._create_development_milestones()

    def _create_validation_experiments(self) -> None:
        """Create experiment specifications for validation."""
        experiments = [
            {
                "type": ExperimentType.BINDING_ASSAY,
                "protocol": {
                    "target": "VDAC1",
                    "method": "SPR_analysis",
                    "cbd_concentrations": [1, 5, 10, 25, 50, 100],  # μM
                    "duration": "real_time_kinetics"
                },
                "expected_outcomes": {
                    "kd_range": "5-25 μM",
                    "binding_stoichiometry": "1:1",
                    "off_rate": "< 0.1 s-1"
                },
                "success_criteria": {
                    "kd_in_range": True,
                    "specific_binding": "> 80%",
                    "reproducibility": "> 0.9"
                },
                "priority_score": 0.9,
                "estimated_duration": 14
            },
            {
                "type": ExperimentType.SELECTIVITY,
                "protocol": {
                    "cell_lines": ["U87MG", "normal_astrocytes", "HEK293"],
                    "cbd_concentrations": [1, 5, 10, 25, 50],
                    "timepoints": [24, 48, 72],  # hours
                    "readouts": ["viability", "apoptosis", "ROS_levels"]
                },
                "expected_outcomes": {
                    "selectivity_index": "2.1-2.8",
                    "ic50_glioma": "10-20 μM",
                    "ic50_normal": "> 40 μM"
                },
                "success_criteria": {
                    "selectivity_achieved": True,
                    "ros_correlation": "> 0.7",
                    "dose_response": "sigmoidal"
                },
                "priority_score": 0.95,
                "estimated_duration": 21
            },
            {
                "type": ExperimentType.BIOMARKER,
                "protocol": {
                    "target": "TRPV4",
                    "assays": ["qPCR", "Western_blot", "flow_cytometry"],
                    "treatment_groups": ["vehicle", "cbd_10uM", "cbd_25uM"],
                    "timepoints": [6, 12, 24, 48]  # hours
                },
                "expected_outcomes": {
                    "expression_change": "2-5 fold",
                    "dose_dependency": True,
                    "temporal_pattern": "peak_12-24h"
                },
                "success_criteria": {
                    "significant_change": "p < 0.05",
                    "dose_response": True,
                    "specificity": "> 0.8"
                },
                "priority_score": 0.7,
                "estimated_duration": 28
            },
            {
                "type": ExperimentType.DOSING,
                "protocol": {
                    "pulse_frequencies": [0.5, 1.0, 1.5, 2.0],  # Hz equivalent
                    "continuous_vs_pulsed": True,
                    "total_dose_matched": True,
                    "duration": 72  # hours
                },
                "expected_outcomes": {
                    "optimal_frequency": "1.0-1.5 Hz_equivalent",
                    "pulse_advantage": "> 20% efficacy",
                    "reduced_toxicity": "> 30%"
                },
                "success_criteria": {
                    "frequency_optimum": True,
                    "pulse_superiority": True,
                    "safety_margin": "> 2-fold"
                },
                "priority_score": 0.6,
                "estimated_duration": 35
            }
        ]

        for exp_data in experiments:
            exp = ExperimentSpec(**exp_data)
            self.experiments[exp.id] = exp
            logger.info(f"Created experiment: {exp.type.value}")

    def _create_development_milestones(self) -> None:
        """Create therapeutic development milestones."""
        milestones = [
            {
                "phase": ResearchPhase.DISCOVERY,
                "min_confidence": 0.7,
                "decision_criteria": {
                    "binding_validated": True,
                    "selectivity_confirmed": True,
                    "mechanism_understood": True
                },
                "estimated_timeline": 90
            },
            {
                "phase": ResearchPhase.PRECLINICAL,
                "min_confidence": 0.8,
                "decision_criteria": {
                    "biomarker_validated": True,
                    "dosing_optimized": True,
                    "safety_profile": "acceptable",
                    "efficacy_demonstrated": True
                },
                "estimated_timeline": 180
            },
            {
                "phase": ResearchPhase.PHASE_I,
                "min_confidence": 0.9,
                "decision_criteria": {
                    "safety_established": True,
                    "biomarker_clinical": True,
                    "dose_escalation": "completed"
                },
                "estimated_timeline": 365
            }
        ]

        for milestone_data in milestones:
            milestone = TherapeuticMilestone(**milestone_data)
            self.milestones[milestone.id] = milestone
            logger.info(f"Created milestone: {milestone.phase.value}")

    def update_literature_monitoring(self) -> Dict[str, List[str]]:
        """Simulate literature monitoring and paradigm shift detection."""
        # In production, this would integrate with PubMed, arXiv, etc.
        updates = {
            "new_papers": [
                "CBD-VDAC1 crystal structure reveals allosteric site (2025)",
                "TRPV4-MCU crosstalk mediates CBD selectivity (2025)",
                "Chloride channel CBD binding confirmed via cryo-EM (2025)"
            ],
            "paradigm_shifts": [
                "Mitochondrial CBD uptake mechanism challenges cytosolic model"
            ],
            "contradictions": [
                "Alternative study reports CBD selectivity index 3.2"
            ]
        }

        # Update confidence based on new evidence
        for paper in updates["new_papers"]:
            self._process_literature_update(paper)

        # Flag potential paradigm shifts
        for shift in updates["paradigm_shifts"]:
            self._flag_paradigm_shift(shift)

        return updates

    def _process_literature_update(self, paper_title: str) -> None:
        """Process new literature and update relevant claims."""
        # Simple keyword matching - in production would use NLP
        keywords = {
            "VDAC1": ["binding", "crystal", "structure"],
            "TRPV4": ["biomarker", "MCU", "crosstalk"],
            "selectivity": ["index", "ratio", "glioma"]
        }

        for claim in self.claims.values():
            for keyword, terms in keywords.items():
                if keyword.lower() in claim.description.lower():
                    if any(term in paper_title.lower() for term in terms):
                        claim.update_confidence(paper_title, 0.1)
                        logger.info(f"Updated claim confidence: {claim.description[:30]}...")

    def _flag_paradigm_shift(self, shift_description: str) -> None:
        """Flag potential paradigm shifts requiring attention."""
        logger.warning(f"PARADIGM SHIFT DETECTED: {shift_description}")
        # In production, would trigger expert review workflow

    def calculate_experiment_priority(self, experiment_id: str) -> float:
        """Calculate experiment priority score based on multiple factors."""
        exp = self.experiments[experiment_id]
        weights = self.config["priority_weights"]

        # Therapeutic impact (higher for selectivity, binding)
        impact_scores = {
            ExperimentType.SELECTIVITY: 1.0,
            ExperimentType.BINDING_ASSAY: 0.9,
            ExperimentType.BIOMARKER: 0.7,
            ExperimentType.DOSING: 0.6,
            ExperimentType.MECHANISM: 0.5
        }

        impact = impact_scores.get(exp.type, 0.5)
        feasibility = 1.0 - (exp.estimated_duration / 365)  # Shorter = more feasible
        cost = 0.8  # Placeholder - would integrate actual cost estimates
        timeline = 1.0 - (exp.estimated_duration / 180)  # Favor faster experiments

        priority = (
            weights["therapeutic_impact"] * impact +
            weights["feasibility"] * feasibility +
            weights["cost"] * cost +
            weights["timeline"] * timeline
        )

        exp.priority_score = priority
        return priority

    def generate_research_roadmap(self) -> Dict:
        """Generate prioritized research roadmap with timelines."""
        # Calculate priorities
        for exp_id in self.experiments:
            self.calculate_experiment_priority(exp_id)

        # Sort by priority
        sorted_experiments = sorted(
            self.experiments.items(),
            key=lambda x: x[1].priority_score,
            reverse=True
        )

        roadmap = {
            "phases": [],
            "critical_path": [],
            "total_timeline": 0,
            "confidence_progression": []
        }

        current_date = datetime.now()

        for phase in ResearchPhase:
            phase_experiments = [
                (exp_id, exp) for exp_id, exp in sorted_experiments
                if self._experiment_fits_phase(exp, phase)
            ]

            if phase_experiments:
                phase_data = {
                    "phase": phase.value,
                    "experiments": [exp_id for exp_id, _ in phase_experiments],
                    "duration": max(exp.estimated_duration for _, exp in phase_experiments),
                    "start_date": current_date.isoformat(),
                    "end_date": (current_date + timedelta(days=max(exp.estimated_duration for _, exp in phase_experiments))).isoformat()
                }
                roadmap["phases"].append(phase_data)
                current_date += timedelta(days=phase_data["duration"])

        roadmap["total_timeline"] = (current_date - datetime.now()).days

        return roadmap

    def _experiment_fits_phase(self, experiment: ExperimentSpec, phase: ResearchPhase) -> bool:
        """Determine if experiment fits in research phase."""
        phase_mapping = {
            ResearchPhase.DISCOVERY: [ExperimentType.BINDING_ASSAY, ExperimentType.SELECTIVITY],
            ResearchPhase.PRECLINICAL: [ExperimentType.BIOMARKER, ExperimentType.DOSING, ExperimentType.MECHANISM],
            ResearchPhase.PHASE_I: [],  # Clinical experiments not defined here
        }
        return experiment.type in phase_mapping.get(phase, [])

    def assess_clinical_readiness(self) -> Dict:
        """Assess readiness for clinical development."""
        readiness_score = 0.0
        required_validations = [
            "VDAC1 direct binding validated",
            "ROS-dependent selectivity confirmed",
            "Channel-first mechanism superior"
        ]

        validated_count = 0
        for claim in self.claims.values():
            for requirement in required_validations:
                if requirement.lower() in claim.description.lower():
                    if claim.confidence >= 0.7:
                        validated_count += 1
                        readiness_score += claim.confidence

        readiness_score /= len(required_validations)

        return {
            "readiness_score": readiness_score,
            "validated_requirements": validated_count,
            "total_requirements": len(required_validations),
            "recommendation": "Proceed to preclinical" if readiness_score > 0.7 else "Continue discovery research",
            "blocking_issues": self._identify_blocking_issues()
        }

    def _identify_blocking_issues(self) -> List[str]:
        """Identify issues blocking clinical progression."""
        issues = []

        for claim in self.claims.values():
            if claim.confidence < 0.5 and "mechanism" in claim.description.lower():
                issues.append(f"Low confidence in: {claim.description}")

            if len(claim.contradictions) > self.config["max_contradictions"]:
                issues.append(f"Multiple contradictions for: {claim.description}")

        return issues

    def export_system_state(self, filepath: Path) -> None:
        """Export complete system state for persistence."""
        state = {
            "timestamp": datetime.now().isoformat(),
            "claims": {
                claim_id: {
                    "description": claim.description,
                    "confidence": claim.confidence,
                    "evidence_sources": claim.evidence_sources,
                    "iris_convergence": claim.iris_convergence,
                    "last_validated": claim.last_validated.isoformat() if claim.last_validated else None
                }
                for claim_id, claim in self.claims.items()
            },
            "experiments": {
                exp_id: {
                    "type": exp.type.value,
                    "priority_score": exp.priority_score,
                    "estimated_duration": exp.estimated_duration,
                    "protocol": exp.protocol,
                    "success_criteria": exp.success_criteria
                }
                for exp_id, exp in self.experiments.items()
            }
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f"System state exported to {filepath}")


def main():
    """Main execution function."""
    system = CBDTherapeuticSystem()

    # Update literature monitoring
    updates = system.update_literature_monitoring()
    print(f"Literature updates: {len(updates['new_papers'])} new papers")

    # Generate research roadmap
    roadmap = system.generate_research_roadmap()
    print(f"Research roadmap: {len(roadmap['phases'])} phases, {roadmap['total_timeline']} days total")

    # Assess clinical readiness
    readiness = system.assess_clinical_readiness()
    print(f"Clinical readiness: {readiness['readiness_score']:.2f} ({readiness['recommendation']})")

    # Export state
    output_path = Path("/Users/vaquez/Desktop/iris-gate/cbd_system_state.json")
    system.export_system_state(output_path)

    return system


if __name__ == "__main__":
    system = main()