#!/usr/bin/env python3
"""
Usage examples for CBD Therapeutic Development System
Demonstrates key functionality and typical workflows.
"""

from pathlib import Path
from cbd_therapeutic_system import CBDTherapeuticSystem, ResearchClaim, ExperimentType


def example_basic_usage():
    """Basic system usage example."""
    print("=== CBD Therapeutic Development System - Basic Usage ===\n")

    # Initialize system
    config_path = Path("/Users/vaquez/Desktop/iris-gate/cbd_system_config.json")
    system = CBDTherapeuticSystem(config_path)

    print(f"System initialized with:")
    print(f"  - {len(system.claims)} research claims")
    print(f"  - {len(system.experiments)} validation experiments")
    print(f"  - {len(system.milestones)} development milestones\n")

    return system


def example_literature_monitoring(system):
    """Demonstrate literature monitoring functionality."""
    print("=== Literature Monitoring ===\n")

    # Simulate literature updates
    updates = system.update_literature_monitoring()

    print("Literature monitoring results:")
    print(f"  - New papers: {len(updates['new_papers'])}")
    for paper in updates['new_papers']:
        print(f"    * {paper}")

    print(f"  - Paradigm shifts detected: {len(updates['paradigm_shifts'])}")
    for shift in updates['paradigm_shifts']:
        print(f"    * {shift}")

    print(f"  - Contradictions found: {len(updates['contradictions'])}")
    for contradiction in updates['contradictions']:
        print(f"    * {contradiction}")
    print()


def example_confidence_tracking(system):
    """Demonstrate confidence tracking and updates."""
    print("=== Confidence Tracking ===\n")

    # Show current confidence levels
    print("Current research claim confidence levels:")
    for claim_id, claim in system.claims.items():
        if claim.iris_convergence:  # Focus on IRIS-related claims
            print(f"  - {claim.description[:50]}...")
            print(f"    Confidence: {claim.confidence:.2f}")
            print(f"    IRIS Convergence: {claim.iris_convergence:.2f}")
            print(f"    Evidence sources: {len(claim.evidence_sources)}")
            print()


def example_experiment_prioritization(system):
    """Demonstrate experiment prioritization."""
    print("=== Experiment Prioritization ===\n")

    # Calculate and display priorities
    priorities = []
    for exp_id, exp in system.experiments.items():
        priority = system.calculate_experiment_priority(exp_id)
        priorities.append((exp.type.value, priority, exp.estimated_duration))

    # Sort by priority
    priorities.sort(key=lambda x: x[1], reverse=True)

    print("Prioritized experiments:")
    for exp_type, priority, duration in priorities:
        print(f"  - {exp_type.replace('_', ' ').title()}")
        print(f"    Priority Score: {priority:.2f}")
        print(f"    Estimated Duration: {duration} days")
        print()


def example_research_roadmap(system):
    """Demonstrate research roadmap generation."""
    print("=== Research Roadmap Generation ===\n")

    roadmap = system.generate_research_roadmap()

    print(f"Total development timeline: {roadmap['total_timeline']} days")
    print(f"Number of phases: {len(roadmap['phases'])}")
    print()

    for phase in roadmap['phases']:
        print(f"Phase: {phase['phase'].title()}")
        print(f"  Duration: {phase['duration']} days")
        print(f"  Start: {phase['start_date'][:10]}")
        print(f"  End: {phase['end_date'][:10]}")
        print(f"  Experiments: {len(phase['experiments'])}")
        print()


def example_clinical_readiness(system):
    """Demonstrate clinical readiness assessment."""
    print("=== Clinical Readiness Assessment ===\n")

    readiness = system.assess_clinical_readiness()

    print(f"Overall readiness score: {readiness['readiness_score']:.2f}")
    print(f"Validated requirements: {readiness['validated_requirements']}/{readiness['total_requirements']}")
    print(f"Recommendation: {readiness['recommendation']}")

    if readiness['blocking_issues']:
        print(f"Blocking issues ({len(readiness['blocking_issues'])}):")
        for issue in readiness['blocking_issues']:
            print(f"  - {issue}")
    else:
        print("No blocking issues identified")
    print()


def example_iris_integration():
    """Demonstrate IRIS convergence data integration."""
    print("=== IRIS Integration Example ===\n")

    # Create new IRIS-derived claim
    iris_claim = ResearchClaim(
        description="New IRIS pattern: phase-locked oscillations at 1.2 Hz",
        confidence=0.6,
        iris_convergence=0.88,
        evidence_sources=["IRIS_latest_session"]
    )

    print("New IRIS claim created:")
    print(f"  Description: {iris_claim.description}")
    print(f"  Initial confidence: {iris_claim.confidence}")
    print(f"  IRIS convergence: {iris_claim.iris_convergence}")
    print()

    # Simulate validation with literature
    iris_claim.update_confidence("Phase-locked oscillations in glioma confirmed (Nature 2025)", 0.85)

    print("After literature validation:")
    print(f"  Updated confidence: {iris_claim.confidence:.2f}")
    print(f"  Evidence sources: {len(iris_claim.evidence_sources)}")
    print()


def example_experiment_design():
    """Demonstrate experiment specification."""
    print("=== Experiment Design Example ===\n")

    system = CBDTherapeuticSystem()

    # Show detailed experiment specifications
    for exp_id, exp in list(system.experiments.items())[:2]:  # Show first 2
        print(f"Experiment: {exp.type.value.replace('_', ' ').title()}")
        print(f"  Priority Score: {exp.priority_score:.2f}")
        print(f"  Duration: {exp.estimated_duration} days")
        print("  Protocol highlights:")

        for key, value in list(exp.protocol.items())[:3]:  # Show first 3 protocol items
            print(f"    - {key}: {value}")

        print("  Success criteria:")
        for criterion, requirement in exp.success_criteria.items():
            print(f"    - {criterion}: {requirement}")
        print()


def example_state_export(system):
    """Demonstrate system state export."""
    print("=== System State Export ===\n")

    export_path = Path("/Users/vaquez/Desktop/iris-gate/demo_system_state.json")
    system.export_system_state(export_path)

    print(f"System state exported to: {export_path}")
    print(f"File size: {export_path.stat().st_size} bytes")

    # Show structure
    import json
    with open(export_path) as f:
        state = json.load(f)

    print("Export structure:")
    for key, value in state.items():
        if isinstance(value, dict):
            print(f"  - {key}: {len(value)} items")
        else:
            print(f"  - {key}: {type(value).__name__}")
    print()


def main():
    """Run all usage examples."""
    print("CBD Therapeutic Development System - Usage Examples")
    print("=" * 55)
    print()

    # Initialize system
    system = example_basic_usage()

    # Run examples
    example_literature_monitoring(system)
    example_confidence_tracking(system)
    example_experiment_prioritization(system)
    example_research_roadmap(system)
    example_clinical_readiness(system)
    example_iris_integration()
    example_experiment_design()
    example_state_export(system)

    print("All examples completed successfully!")
    print("\nNext Steps:")
    print("1. Integrate with real literature APIs (PubMed, arXiv)")
    print("2. Connect to laboratory information systems")
    print("3. Add regulatory compliance tracking")
    print("4. Implement resource allocation optimization")
    print("5. Build web interface for stakeholder access")


if __name__ == "__main__":
    main()