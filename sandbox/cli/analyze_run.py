#!/usr/bin/env python3
"""
Analyze Sandbox Experiment Results

Generates plots, summaries, and validation reports from simulation runs.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

def load_results(run_dir: Path) -> dict:
    """Load predictions and config from run directory."""
    predictions_file = run_dir / "predictions.json"
    config_file = run_dir / "config.snapshot.json"

    if not predictions_file.exists():
        raise FileNotFoundError(f"Predictions not found: {predictions_file}")

    with open(predictions_file) as f:
        predictions = json.load(f)

    config = {}
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)

    return {"predictions": predictions, "config": config}

def generate_summary_table(results: dict) -> str:
    """Generate markdown summary table."""

    predictions = results["predictions"]
    consensus = predictions.get("consensus", {})

    lines = [
        "# Sandbox Experiment Summary",
        "",
        f"**Run:** {predictions['plan']['plan_id']}",
        f"**Species:** {predictions['plan']['species']}",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## Consensus Predictions",
        "",
        "| Condition | P(regeneration) | 95% CI | Range | Agreement |",
        "|-----------|----------------|--------|-------|-----------|"
    ]

    for condition in predictions["plan"]["conditions"]:
        label = condition["label"]
        if label in consensus:
            cons = consensus[label].get("regeneration_7d", {})
            p = cons.get("weighted_mean", 0.0)
            std = cons.get("std", 0.0)
            min_val = cons.get("min", 0.0)
            max_val = cons.get("max", 0.0)
            agreement = cons.get("agreement", 0.0)

            ci = f"[{p-1.96*std:.3f}, {p+1.96*std:.3f}]"
            range_str = f"[{min_val:.3f}, {max_val:.3f}]"

            lines.append(
                f"| {label} | {p:.3f} | {ci} | {range_str} | {agreement:.2f} |"
            )

    lines.extend([
        "",
        "## Per-Mirror Results",
        ""
    ])

    # Show variance across mirrors
    for condition in predictions["plan"]["conditions"]:
        label = condition["label"]
        lines.append(f"### {label}")
        lines.append("")

        mirror_values = []
        for mirror, results_dict in predictions["mirrors"].items():
            if label in results_dict:
                p_regen = results_dict[label]["outcomes"]["regeneration_7d"]["mean"]
                ci_lower = results_dict[label]["outcomes"]["regeneration_7d"]["ci_lower"]
                ci_upper = results_dict[label]["outcomes"]["regeneration_7d"]["ci_upper"]
                mirror_values.append((mirror, p_regen, ci_lower, ci_upper))

        for mirror, p, ci_l, ci_u in sorted(mirror_values, key=lambda x: x[1], reverse=True):
            lines.append(f"- **{mirror}**: {p:.3f} [{ci_l:.3f}, {ci_u:.3f}]")

        lines.append("")

    return "\n".join(lines)

def generate_onepager(results: dict, output_file: Path):
    """Generate one-page summary for collaborators."""

    predictions = results["predictions"]
    plan = predictions["plan"]

    lines = [
        f"# {plan['plan_id']} — One-Pager",
        "",
        "## Experiment Design",
        f"- **System:** {plan.get('species', 'unspecified')}",
        f"- **Hypothesis:** {plan.get('description', 'N/A')}",
        f"- **Mirrors:** {len(plan['mirrors'])} AI architectures (1.7B-671B parameters)",
        f"- **Conditions:** {len(plan['conditions'])}",
        f"- **Monte Carlo runs:** {plan.get('runs', 'N/A')} per condition per mirror",
        "",
        "## Key Predictions",
        ""
    ]

    consensus = predictions.get("consensus", {})

    # Sort conditions by P(regen)
    condition_probs = []
    for condition in plan["conditions"]:
        label = condition["label"]
        if label in consensus:
            p = consensus[label]["regeneration_7d"]["weighted_mean"]
            condition_probs.append((label, p, condition.get("description", "")))

    condition_probs.sort(key=lambda x: x[1], reverse=True)

    for label, p, desc in condition_probs:
        lines.append(f"### {label}: P(regen) = {p:.3f}")
        if desc:
            lines.append(f"*{desc}*")
        lines.append("")

    lines.extend([
        "## How to Falsify",
        "",
        "**Wet-lab protocol:**",
        f"1. {plan.get('species', 'Model organism')} amputation/injury",
        "2. Apply perturbations at doses specified in plan",
        f"3. Measure readouts: {', '.join(plan.get('readouts', []))}",
        f"4. Score regeneration at {max(plan.get('timepoints_hr', [168]))/24:.0f}d",
        "",
        "**Decision rules:**",
        "- If P(regen) matches predictions (±0.10): Model validated, perturbations weak → escalate doses",
        "- If P(regen) << predictions (e.g., 0.30 vs 0.95): Model underestimates triple co-requirement → refine priors",
        "- If P(regen) >> predictions: Model overestimates perturbation effects → reduce deltas",
        "",
        "## Provenance",
        f"- **S4 source:** {results['config'].get('plan', {}).get('provenance', {}).get('source_session', 'N/A')}",
        f"- **Literature grounding:** {results['config'].get('plan', {}).get('provenance', {}).get('literature_grounding', 'N/A')}",
        f"- **Created:** {results['config'].get('execution_timestamp', 'N/A')}",
        "",
        "**†⟡∞ Generated by IRIS Sandbox Simulator**"
    ])

    with open(output_file, "w") as f:
        f.write("\n".join(lines))

    print(f"✓ One-pager saved to {output_file}")

def generate_comparison_table(run_dirs: list) -> str:
    """Compare multiple runs side-by-side."""

    lines = [
        "# Run Comparison",
        "",
        "| Run | WT | Center- | Rhythm- | Aperture- | Rhythm-+Aperture- |",
        "|-----|----|---------|---------|-----------|--------------------|"
    ]

    for run_dir in run_dirs:
        results = load_results(Path(run_dir))
        consensus = results["predictions"].get("consensus", {})

        run_name = Path(run_dir).name

        values = []
        for label in ["WT", "Center-", "Rhythm-", "Aperture-", "Rhythm- Aperture-"]:
            if label in consensus:
                p = consensus[label]["regeneration_7d"]["weighted_mean"]
                values.append(f"{p:.3f}")
            else:
                values.append("N/A")

        lines.append(f"| {run_name} | {' | '.join(values)} |")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Analyze sandbox experiment results")
    parser.add_argument(
        "--run",
        type=Path,
        help="Run directory to analyze"
    )
    parser.add_argument(
        "--last",
        action="store_true",
        help="Analyze most recent run"
    )
    parser.add_argument(
        "--summary",
        choices=["table", "onepager", "full"],
        default="table",
        help="Type of summary to generate"
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        help="Compare multiple runs"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file (default: stdout)"
    )

    args = parser.parse_args()

    # Find run directory
    if args.last:
        runs_dir = Path("sandbox/runs/outputs")
        run_dirs = sorted(runs_dir.glob("RUN_*"), key=lambda p: p.name, reverse=True)
        if not run_dirs:
            print("ERROR: No runs found in sandbox/runs/outputs/")
            sys.exit(1)
        run_dir = run_dirs[0]
        print(f"Analyzing most recent run: {run_dir.name}")
    elif args.run:
        run_dir = args.run
    elif args.compare:
        # Comparison mode
        comparison = generate_comparison_table(args.compare)
        print(comparison)
        if args.output:
            args.output.write_text(comparison)
        return
    else:
        print("ERROR: Specify --run or --last")
        sys.exit(1)

    # Load results
    try:
        results = load_results(run_dir)
    except Exception as e:
        print(f"ERROR: Failed to load results: {e}")
        sys.exit(1)

    # Generate output
    if args.summary == "table":
        output = generate_summary_table(results)
        print(output)
        if args.output:
            args.output.write_text(output)

    elif args.summary == "onepager":
        if not args.output:
            args.output = run_dir / "ONEPAGER.md"
        generate_onepager(results, args.output)

    elif args.summary == "full":
        # Generate all outputs
        table_file = run_dir / "SUMMARY.md"
        onepager_file = run_dir / "ONEPAGER.md"

        table_file.write_text(generate_summary_table(results))
        print(f"✓ Summary table: {table_file}")

        generate_onepager(results, onepager_file)
        print(f"✓ One-pager: {onepager_file}")

if __name__ == "__main__":
    main()
