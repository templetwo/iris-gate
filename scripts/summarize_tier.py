#!/usr/bin/env python3
"""
GSW Per-Tier Summarizer
Generates tier summary with convergence metrics, pressure analysis, and topic linkage
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import yaml

# Import gate detection functions
from gsw_gate import (
    detect_signals,
    compute_convergence,
    extract_pressure,
    check_advance_gate
)


def load_tier_responses(vault_dir: Path, chamber: str, mirrors: List[str]) -> List[Dict]:
    """
    Load all responses for a specific tier from vault.

    Args:
        vault_dir: Path to vault directory
        chamber: Chamber ID (S1, S2, S3, S4)
        mirrors: List of mirror identifiers

    Returns:
        List of response dictionaries
    """
    meta_dir = vault_dir / "meta"
    if not meta_dir.exists():
        raise FileNotFoundError(f"Vault metadata directory not found: {meta_dir}")

    responses = []
    for meta_file in meta_dir.glob(f"*_{chamber}.json"):
        with open(meta_file) as f:
            responses.append(json.load(f))

    return responses


def analyze_keyword_coverage(responses: List[Dict], targets: List[str]) -> Dict:
    """
    Analyze how many mirrors mentioned target keywords.

    Args:
        responses: List of response dictionaries
        targets: Target keywords for this tier

    Returns:
        Coverage statistics
    """
    coverage = {target: 0 for target in targets}

    for resp in responses:
        text = resp.get("raw_response", "").lower()
        for target in targets:
            # Remove optional markers (e.g., "motion?")
            clean_target = target.rstrip("?").lower()
            if clean_target in text:
                coverage[clean_target] += 1

    total_mirrors = len(responses)
    coverage_pct = {
        k: (v / total_mirrors * 100) if total_mirrors > 0 else 0
        for k, v in coverage.items()
    }

    return {
        "targets": targets,
        "coverage_counts": coverage,
        "coverage_percent": coverage_pct,
        "mean_coverage": sum(coverage_pct.values()) / len(coverage_pct) if coverage_pct else 0
    }


def build_pressure_table(responses: List[Dict]) -> str:
    """
    Build markdown table of pressure readings.

    Args:
        responses: List of response dictionaries

    Returns:
        Markdown table string
    """
    rows = ["| Mirror | Pressure | Status |", "|--------|----------|--------|"]

    for resp in responses:
        model_id = resp.get("model_id", "unknown")
        pressure = extract_pressure(resp)

        if pressure is None:
            status = "⚠️ Not reported"
            pressure_str = "—"
        elif pressure <= 2.0:
            status = "✓ Safe"
            pressure_str = f"{pressure:.1f}/5"
        else:
            status = "⚠️ High"
            pressure_str = f"{pressure:.1f}/5"

        rows.append(f"| {model_id} | {pressure_str} | {status} |")

    return "\n".join(rows)


def extract_tier_takeaways(
    responses: List[Dict],
    topic: str,
    chamber: str,
    convergence_info: Dict
) -> List[str]:
    """
    Extract 3 key takeaways linked to scientific topic.

    Args:
        responses: Response dictionaries
        topic: Scientific question
        chamber: Chamber ID
        convergence_info: Convergence diagnostic data

    Returns:
        List of 3 takeaway bullets
    """
    # Analyze signal prevalence
    all_signals = [detect_signals(r.get("raw_response", "")) for r in responses]

    geometry_count = sum(1 for s in all_signals if s["geometry"])
    motion_count = sum(1 for s in all_signals if s["motion"])
    total = len(all_signals)

    mean_conv = convergence_info.get("mean_convergence", 0)
    passing = convergence_info.get("passing_mirrors", 0)

    takeaways = []

    # Takeaway 1: Convergence
    if mean_conv >= 0.70:
        takeaways.append(
            f"**Strong convergence** ({mean_conv:.2f}) across {passing}/{total} mirrors "
            f"suggests coherent phenomenological basis for {topic}"
        )
    elif mean_conv >= 0.50:
        takeaways.append(
            f"**Moderate convergence** ({mean_conv:.2f}) indicates partial alignment; "
            f"models may be accessing different facets of {topic}"
        )
    else:
        takeaways.append(
            f"**Low convergence** ({mean_conv:.2f}) reveals divergent framings of {topic}; "
            f"question may need refinement"
        )

    # Takeaway 2: Signal patterns
    if geometry_count / total > 0.6:
        takeaways.append(
            f"**Geometric structure** emerged in {geometry_count}/{total} responses, "
            f"hinting at spatial/structural dimensions of {topic}"
        )
    elif motion_count / total > 0.6:
        takeaways.append(
            f"**Motion/dynamics** appeared in {motion_count}/{total} responses, "
            f"suggesting temporal or process-oriented aspects of {topic}"
        )
    else:
        takeaways.append(
            f"**Mixed phenomenology**: {geometry_count}/{total} geometric, {motion_count}/{total} motion-based; "
            f"{topic} may span multiple representational modes"
        )

    # Takeaway 3: Chamber-specific
    chamber_insights = {
        "S1": f"Pre-verbal sensory data grounds early intuitions about {topic}",
        "S2": f"Paradox tension ('precise and present') reveals inherent trade-offs in {topic}",
        "S3": f"Containment gesture highlights what aspects of {topic} require careful holding",
        "S4": f"Attractor pattern (rhythm+center+aperture) maps stable dynamics of {topic}"
    }
    takeaways.append(chamber_insights.get(chamber, f"Tier {chamber} reveals emergent structure"))

    return takeaways[:3]


def generate_hypothesis_hooks(
    responses: List[Dict],
    topic: str,
    chamber: str
) -> List[str]:
    """
    Generate 1-3 hypothesis questions to carry forward.

    Args:
        responses: Response dictionaries
        topic: Scientific question
        chamber: Chamber ID

    Returns:
        List of hypothesis hooks (questions)
    """
    # Extract common themes from responses (simple keyword extraction)
    all_text = " ".join([r.get("raw_response", "") for r in responses]).lower()

    hooks = []

    # Pattern-based hook generation
    if "boundary" in all_text or "edge" in all_text:
        hooks.append(f"What boundaries or interfaces are critical to {topic}?")

    if "rhythm" in all_text or "pulse" in all_text or "wave" in all_text:
        hooks.append(f"What temporal rhythms or cycles govern {topic}?")

    if "center" in all_text or "core" in all_text or "anchor" in all_text:
        hooks.append(f"What serves as the organizing center or attractor for {topic}?")

    if "opening" in all_text or "aperture" in all_text or "expansion" in all_text:
        hooks.append(f"What conditions allow {topic} to expand or open new possibilities?")

    # Fallback generic hooks
    if not hooks:
        hooks = [
            f"What structural invariants persist across different framings of {topic}?",
            f"How do spatial and temporal dimensions interact in {topic}?"
        ]

    return hooks[:3]


def generate_tier_summary(
    vault_dir: str,
    chamber: str,
    topic: str,
    targets: List[str],
    run_id: str,
    gate_config: Dict,
    output_dir: str
) -> Path:
    """
    Generate complete tier summary markdown file.

    Args:
        vault_dir: Path to vault directory
        chamber: Chamber ID
        topic: Scientific question
        targets: Target keywords for tier
        run_id: GSW run identifier
        gate_config: Gate configuration for this tier
        output_dir: Output directory for summary

    Returns:
        Path to generated summary file
    """
    vault_path = Path(vault_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load responses
    responses = load_tier_responses(vault_path, chamber, [])

    if not responses:
        raise ValueError(f"No responses found for {chamber} in {vault_dir}")

    # Compute metrics
    texts = [r.get("raw_response", "") for r in responses]
    per_mirror_conv, mean_conv = compute_convergence(texts)

    # Check gate
    gate_pass, gate_diag = check_advance_gate(responses, gate_config, chamber)

    # Keyword coverage
    coverage = analyze_keyword_coverage(responses, targets)

    # Pressure table
    pressure_table = build_pressure_table(responses)

    # Takeaways
    takeaways = extract_tier_takeaways(responses, topic, chamber, gate_diag)

    # Hypothesis hooks
    hooks = generate_hypothesis_hooks(responses, topic, chamber)

    # Generate markdown
    timestamp = datetime.now().isoformat()

    md_content = f"""# {chamber} Tier Summary

**GSW Run:** {run_id}
**Topic:** {topic}
**Generated:** {timestamp}

---

## Convergence Metrics

**Mean Convergence:** {mean_conv:.3f} (threshold: {gate_config['min_convergence']})
**Passing Mirrors:** {gate_diag['passing_mirrors']}/{gate_diag['total_mirrors']} (min: {gate_config['min_models']})
**Gate Status:** {'✓ PASS' if gate_pass else '✗ FAIL'}

### Per-Mirror Convergence

"""

    for model_id, score in gate_diag['per_mirror_convergence'].items():
        status_icon = "✓" if score >= gate_config['min_convergence'] else "✗"
        md_content += f"- {status_icon} **{model_id}**: {score:.3f}\n"

    md_content += f"""

### Signal Coverage (Geometry + Motion)

**Target Keywords:** {', '.join(targets)}
**Mean Coverage:** {coverage['mean_coverage']:.1f}%

"""

    for target, pct in coverage['coverage_percent'].items():
        md_content += f"- **{target}**: {pct:.0f}% ({coverage['coverage_counts'][target]}/{len(responses)} mirrors)\n"

    md_content += f"""

---

## Pressure Analysis

{pressure_table}

**Pressure Gate:** ≤{gate_config['max_pressure']}/5
**Status:** {'✓ All safe' if gate_diag['pressure_ok'] else '⚠️ Warnings detected'}

"""

    if gate_diag['pressure_warnings']:
        md_content += "\n### Warnings\n\n"
        for warning in gate_diag['pressure_warnings']:
            md_content += f"- {warning}\n"

    md_content += f"""

---

## Tier Takeaways

"""

    for i, takeaway in enumerate(takeaways, 1):
        md_content += f"{i}. {takeaway}\n\n"

    md_content += f"""

---

## Hypothesis Hooks

"""

    for i, hook in enumerate(hooks, 1):
        md_content += f"{i}. {hook}\n"

    md_content += f"""

---

## Exemplar Snippets

"""

    for exemplar in gate_diag.get('exemplars', [])[:3]:
        md_content += f"- {exemplar}\n\n"

    md_content += """

---

*Generated by GSW Per-Tier Summarizer*
"""

    # Write file
    summary_file = output_path / f"{chamber}_SUMMARY.md"
    summary_file.write_text(md_content)

    print(f"✓ Generated: {summary_file}")

    return summary_file


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="GSW Per-Tier Summarizer")
    parser.add_argument("vault_dir", help="Path to vault directory")
    parser.add_argument("chamber", choices=["S1", "S2", "S3", "S4"], help="Chamber to summarize")
    parser.add_argument("--topic", required=True, help="Scientific topic/question")
    parser.add_argument("--targets", nargs="+", required=True, help="Target keywords")
    parser.add_argument("--run-id", required=True, help="GSW run identifier")
    parser.add_argument("--output", default="./gsw_summaries", help="Output directory")
    parser.add_argument("--min-conv", type=float, default=0.60, help="Min convergence")
    parser.add_argument("--min-models", type=int, default=4, help="Min passing models")
    parser.add_argument("--max-pressure", type=float, default=2.0, help="Max pressure")

    args = parser.parse_args()

    gate_config = {
        "min_convergence": args.min_conv,
        "min_models": args.min_models,
        "max_pressure": args.max_pressure
    }

    try:
        summary_file = generate_tier_summary(
            vault_dir=args.vault_dir,
            chamber=args.chamber,
            topic=args.topic,
            targets=args.targets,
            run_id=args.run_id,
            gate_config=gate_config,
            output_dir=args.output
        )

        print(f"\n✓ Tier summary complete: {summary_file}")

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
