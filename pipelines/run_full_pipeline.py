#!/usr/bin/env python3
"""
IRIS Full Pipeline Orchestrator

Runs the complete workflow from S4 convergence → simulation → reports.

Usage:
    python pipelines/run_full_pipeline.py \\
        --topic "Your question here" \\
        --id EXP_SLUG \\
        --factor aperture \\
        --turns 100

This script orchestrates:
    1. S1→S4 convergence run (bioelectric_chambered.py)
    2. S4 prior extraction (extract_s4_states.py)
    3. Sandbox simulation (run_plan.py)
    4. Report generation (analyze_run.py)
    5. Pre-registration draft creation
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def run_command(cmd, description, cwd=None):
    """Run shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")

    start_time = time.time()
    result = subprocess.run(cmd, cwd=cwd, capture_output=False)
    elapsed = time.time() - start_time

    if result.returncode != 0:
        print(f"\n❌ Failed: {description} (exit code {result.returncode})")
        sys.exit(1)

    print(f"\n✅ Completed in {elapsed:.1f}s: {description}")
    return result


def run_full_pipeline(
    topic,
    exp_id,
    factor="aperture",
    organism="planaria",
    turns=100,
    mirrors="all",
    mc_runs=300,
    skip_s4=False,
    skip_sim=False
):
    """Execute complete IRIS pipeline."""

    print(f"""
╔══════════════════════════════════════════════════════════╗
║           IRIS Full Pipeline Orchestrator                ║
╠══════════════════════════════════════════════════════════╣
║  Experiment: {exp_id:<43} ║
║  Topic: {topic[:47]:<50} ║
║  Factor: {factor:<47} ║
║  Turns: {turns:<48} ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Phase 0: Create experiment scaffold
    print("\n📋 Phase 0: Creating experiment scaffold...")
    from new_experiment import create_experiment_scaffold

    exp_path = create_experiment_scaffold(
        topic=topic,
        exp_id=exp_id,
        organism=organism,
        factor=factor
    )

    # Phase 1: S4 Convergence
    if not skip_s4:
        print("\n🧠 Phase 1: Running S4 convergence (S1→S2→S3→S4)...")

        cmd = [
            "python3", "-u", "scripts/bioelectric_chambered.py",
            "--turns", str(turns),
            "--topic", topic
        ]

        run_command(
            cmd,
            f"S4 convergence ({turns} turns)",
            cwd=Path.cwd()
        )

        # Find latest session
        vault_dir = Path("iris_vault/scrolls")
        session_dirs = sorted(vault_dir.glob("BIOELECTRIC_CHAMBERED_*"))
        if not session_dirs:
            print("❌ No S4 session found in iris_vault/scrolls/")
            sys.exit(1)

        session_id = session_dirs[-1].name
        print(f"✅ Session complete: {session_id}")
    else:
        print("\n⏭️  Skipping S4 convergence (--skip-s4)")
        # Find latest session
        vault_dir = Path("iris_vault/scrolls")
        session_dirs = sorted(vault_dir.glob("BIOELECTRIC_CHAMBERED_*"))
        session_id = session_dirs[-1].name if session_dirs else "UNKNOWN"

    # Phase 2: Extract S4 Priors
    print("\n🔍 Phase 2: Extracting S4 computational priors...")

    cmd = [
        "python3", "sandbox/cli/extract_s4_states.py",
        "--session", session_id,
        "--output", "sandbox/states"
    ]

    run_command(
        cmd,
        "S4 prior extraction",
        cwd=Path.cwd()
    )

    # Verify priors were created
    priors_dir = Path("sandbox/states")
    prior_files = list(priors_dir.glob("s4_state.*.json"))
    print(f"✅ Created {len(prior_files)} S4 prior files")

    # Phase 3: Run Sandbox Simulation
    if not skip_sim:
        print("\n🧪 Phase 3: Running sandbox simulation...")

        plan_file = exp_path / f"{exp_id}_minimal_plan.yaml"

        # Update plan with session ID
        with open(plan_file, "r") as f:
            plan_content = f.read()
        plan_content = plan_content.replace("AUTO_FILLED_FROM_S4", session_id)
        plan_content = plan_content.replace("AUTO_FILLED", datetime.now().strftime("%Y-%m-%d"))
        with open(plan_file, "w") as f:
            f.write(plan_content)

        cmd = [
            "python3", "sandbox/cli/run_plan.py",
            str(plan_file)
        ]

        run_command(
            cmd,
            f"Monte Carlo simulation ({mc_runs} runs × 7 mirrors)",
            cwd=Path.cwd()
        )

        # Find latest run
        runs_dir = Path("sandbox/runs/outputs")
        run_dirs = sorted(runs_dir.glob("RUN_*"))
        if not run_dirs:
            print("❌ No simulation output found")
            sys.exit(1)

        run_id = run_dirs[-1].name
        print(f"✅ Simulation complete: {run_id}")
    else:
        print("\n⏭️  Skipping simulation (--skip-sim)")
        runs_dir = Path("sandbox/runs/outputs")
        run_dirs = sorted(runs_dir.glob("RUN_*"))
        run_id = run_dirs[-1].name if run_dirs else "UNKNOWN"

    # Phase 4: Generate Reports
    print("\n📊 Phase 4: Generating reports...")

    run_dir = Path("sandbox/runs/outputs") / run_id

    cmd = [
        "python3", "sandbox/cli/analyze_run.py",
        str(run_dir),
        "--output", str(exp_path / "reports")
    ]

    run_command(
        cmd,
        "Report generation",
        cwd=Path.cwd()
    )

    # Phase 5: Update Metadata
    print("\n📝 Phase 5: Updating experiment metadata...")

    metadata_file = exp_path / "metadata.json"
    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    metadata.update({
        "session_id": session_id,
        "run_id": run_id,
        "status": "simulation_complete",
        "updated": datetime.now().isoformat()
    })

    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    # Phase 6: Summary
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                 🎉 Pipeline Complete!                    ║
╠══════════════════════════════════════════════════════════╣
║  Session: {session_id:<46} ║
║  Run: {run_id:<50} ║
║  Reports: {str(exp_path / 'reports'):<46} ║
╠══════════════════════════════════════════════════════════╣
║  📋 Next Steps:                                          ║
║  1. Review reports in {exp_path}/reports/                ║
║  2. Check consensus in consensus_report.md               ║
║  3. Customize pre-registration in prereg_draft.md       ║
║  4. Submit to OSF/AsPredicted                            ║
║  5. Plan wet-lab validation                              ║
╚══════════════════════════════════════════════════════════╝
    """)

    return {
        "exp_id": exp_id,
        "session_id": session_id,
        "run_id": run_id,
        "exp_path": str(exp_path)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run full IRIS pipeline from S4 → simulation → reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline with 100-turn S4 run:
  python pipelines/run_full_pipeline.py \\
      --topic "Does gap junction coupling affect planarian regeneration?" \\
      --id APERTURE_REGEN --factor aperture --turns 100

  # Use existing S4 session, just run simulation:
  python pipelines/run_full_pipeline.py \\
      --topic "..." --id TEST --skip-s4

  # Generate reports from existing simulation:
  python pipelines/run_full_pipeline.py \\
      --topic "..." --id TEST --skip-s4 --skip-sim
        """
    )

    parser.add_argument(
        "--topic",
        required=True,
        help="Research question in 1-2 sentences"
    )
    parser.add_argument(
        "--id",
        required=True,
        help="Experiment ID (slug format, e.g., APERTURE_REGEN)"
    )
    parser.add_argument(
        "--factor",
        choices=["aperture", "rhythm", "center"],
        default="aperture",
        help="Primary factor to test (default: aperture)"
    )
    parser.add_argument(
        "--organism",
        default="planaria",
        help="Organism system (default: planaria)"
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=100,
        help="Number of IRIS turns for S4 convergence (default: 100)"
    )
    parser.add_argument(
        "--mirrors",
        default="all",
        help="Mirrors to use (all | high_capacity | local_only)"
    )
    parser.add_argument(
        "--mc-runs",
        type=int,
        default=300,
        help="Monte Carlo runs per condition (default: 300)"
    )
    parser.add_argument(
        "--skip-s4",
        action="store_true",
        help="Skip S4 convergence run (use latest session)"
    )
    parser.add_argument(
        "--skip-sim",
        action="store_true",
        help="Skip simulation (use latest run)"
    )

    args = parser.parse_args()

    result = run_full_pipeline(
        topic=args.topic,
        exp_id=args.id,
        factor=args.factor,
        organism=args.organism,
        turns=args.turns,
        mirrors=args.mirrors,
        mc_runs=args.mc_runs,
        skip_s4=args.skip_s4,
        skip_sim=args.skip_sim
    )

    print(f"\n✅ All done! Experiment data: {result}")


if __name__ == "__main__":
    main()
