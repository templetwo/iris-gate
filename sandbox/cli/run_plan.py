#!/usr/bin/env python3
"""
Sandbox Experiment Runner

Main CLI tool to execute experiment plans using Monte Carlo simulations
across all mirrors with consensus analysis.

Usage:
    python sandbox/cli/run_plan.py --plan sandbox/runs/plans/sandbox_plan_planaria.yaml
"""

import argparse
import json
import yaml
import sys
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent / "engines" / "simulators"))
sys.path.append(str(Path(__file__).parent.parent / "engines" / "consensus"))

from monte_carlo import MonteCarloEngine
from mirror_vote import MirrorConsensus

def load_plan(plan_file: Path) -> dict:
    """Load experiment plan YAML."""
    with open(plan_file) as f:
        return yaml.safe_load(f)

def run_experiment(plan_file: Path, output_dir: Path = None):
    """Execute full experiment plan."""

    print("="*60)
    print("IRIS Sandbox Experiment Simulator")
    print("="*60)
    print()

    # Load plan
    plan = load_plan(plan_file)
    print(f"Plan: {plan.get('plan_id', 'UNNAMED')}")
    print(f"Species: {plan.get('species', 'unspecified')}")
    print(f"Mirrors: {len(plan['mirrors'])}")
    print(f"Conditions: {len(plan['conditions'])}")
    print(f"Monte Carlo runs: {plan.get('runs', 500)}")
    print()

    # Create output directory
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"sandbox/runs/outputs/RUN_{timestamp}")

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    print()

    # Initialize engine
    print("Initializing Monte Carlo engine...")
    config = {}
    engine = MonteCarloEngine(config)
    print(f"  ✓ Loaded {len(engine.s4_states)} S4 states")
    print()

    # Run simulations
    print("Running simulations...")
    results = engine.run_full_experiment(plan, output_dir)

    # Generate consensus report
    print("\nGenerating consensus report...")

    # Extract mirror confidences
    mirror_confidences = {
        mirror: engine.s4_states[mirror]["confidence"]
        for mirror in plan["mirrors"]
    }

    consensus_analyzer = MirrorConsensus(mirror_confidences)

    condition_labels = [c["label"] for c in plan["conditions"]]
    consensus_report = consensus_analyzer.generate_consensus_report(results, condition_labels)

    # Save consensus report
    consensus_file = output_dir / "consensus_report.md"
    with open(consensus_file, "w") as f:
        f.write(consensus_report)

    print(f"  ✓ Consensus report saved to {consensus_file}")

    # Save config snapshot
    config_snapshot = {
        "plan": plan,
        "execution_timestamp": datetime.now().isoformat(),
        "s4_states_snapshot": {
            mirror: {
                "confidence": engine.s4_states[mirror]["confidence"],
                "provenance_hash": engine.s4_states[mirror]["provenance_hash"],
                "n_s4_scrolls": engine.s4_states[mirror]["n_s4_scrolls"]
            }
            for mirror in plan["mirrors"]
        }
    }

    config_snapshot_file = output_dir / "config.snapshot.json"
    with open(config_snapshot_file, "w") as f:
        json.dump(config_snapshot, f, indent=2)

    print(f"  ✓ Config snapshot saved to {config_snapshot_file}")

    # Print summary
    print()
    print("="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print()
    print("Results:")
    print(f"  - Predictions: {output_dir / 'predictions.json'}")
    print(f"  - Consensus report: {output_dir / 'consensus_report.md'}")
    print(f"  - Config snapshot: {output_dir / 'config.snapshot.json'}")
    print()

    # Print quick summary of consensus
    print("Quick Summary:")
    print()

    for condition in plan["conditions"]:
        label = condition["label"]
        if label in results["consensus"]:
            cons = results["consensus"][label]["regeneration_7d"]
            print(f"  {label}:")
            print(f"    P(regen) = {cons['weighted_mean']:.3f} ± {cons['std']:.3f}")
            print(f"    Range: [{cons['min']:.3f}, {cons['max']:.3f}]")
            print(f"    Agreement: {cons.get('agreement', 'N/A'):.2f}")
            print()

    print("="*60)
    print()

    return results

def main():
    parser = argparse.ArgumentParser(description="Run sandbox experiment plan")
    parser.add_argument(
        "--plan",
        type=Path,
        required=True,
        help="Path to experiment plan YAML file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory (default: auto-generated timestamp)"
    )

    args = parser.parse_args()

    if not args.plan.exists():
        print(f"ERROR: Plan file not found: {args.plan}")
        sys.exit(1)

    try:
        run_experiment(args.plan, args.output)
    except Exception as e:
        print(f"\nERROR: Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
