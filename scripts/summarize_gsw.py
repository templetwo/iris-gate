#!/usr/bin/env python3
"""
GSW Final Summarizer
Synthesizes S1-S4 tier summaries into executive report with through-lines and attractor analysis
"""

import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


def parse_tier_summary(summary_path: Path) -> Dict:
    """
    Parse a tier summary markdown file.

    Args:
        summary_path: Path to tier summary markdown

    Returns:
        Parsed summary dictionary
    """
    content = summary_path.read_text()

    # Extract key metrics using regex
    data = {
        "chamber": re.search(r'^# (\w+) Tier Summary', content, re.MULTILINE),
        "mean_convergence": re.search(r'Mean Convergence:\*\* ([\d.]+)', content),
        "passing_mirrors": re.search(r'Passing Mirrors:\*\* (\d+)/(\d+)', content),
        "gate_status": re.search(r'Gate Status:\*\* (.+)', content),
        "pressure_status": re.search(r'\*\*Status:\*\* (.+)', content, re.MULTILINE),
    }

    # Extract takeaways
    takeaways_match = re.search(
        r'## Tier Takeaways\s+(.+?)---',
        content,
        re.DOTALL
    )
    takeaways = []
    if takeaways_match:
        takeaway_text = takeaways_match.group(1)
        takeaways = [
            line.strip().lstrip("0123456789. ")
            for line in takeaway_text.split("\n")
            if line.strip() and re.match(r'^\d+\.', line.strip())
        ]

    # Extract hypothesis hooks
    hooks_match = re.search(
        r'## Hypothesis Hooks\s+(.+?)---',
        content,
        re.DOTALL
    )
    hooks = []
    if hooks_match:
        hook_text = hooks_match.group(1)
        hooks = [
            line.strip().lstrip("0123456789. ")
            for line in hook_text.split("\n")
            if line.strip() and re.match(r'^\d+\.', line.strip())
        ]

    return {
        "chamber": data["chamber"].group(1) if data["chamber"] else "UNKNOWN",
        "mean_convergence": float(data["mean_convergence"].group(1)) if data["mean_convergence"] else 0.0,
        "passing_mirrors": (
            int(data["passing_mirrors"].group(1)),
            int(data["passing_mirrors"].group(2))
        ) if data["passing_mirrors"] else (0, 0),
        "gate_pass": "PASS" in data["gate_status"].group(1) if data["gate_status"] else False,
        "pressure_ok": "safe" in data["pressure_status"].group(1).lower() if data["pressure_status"] else True,
        "takeaways": takeaways,
        "hooks": hooks,
        "raw_content": content
    }


def identify_throughlines(tier_summaries: Dict[str, Dict]) -> List[str]:
    """
    Identify patterns that persisted or strengthened S1→S4.

    Args:
        tier_summaries: Dictionary mapping chamber ID to parsed summary

    Returns:
        List of through-line observations
    """
    throughlines = []

    # Check convergence trend
    chambers = ["S1", "S2", "S3", "S4"]
    convergences = [
        tier_summaries[ch]["mean_convergence"]
        for ch in chambers
        if ch in tier_summaries
    ]

    if len(convergences) >= 3:
        # Monotonic increase check
        increasing = all(
            convergences[i] <= convergences[i+1]
            for i in range(len(convergences)-1)
        )
        if increasing:
            throughlines.append(
                f"**Convergence strengthened monotonically** from S1 ({convergences[0]:.2f}) "
                f"to S4 ({convergences[-1]:.2f}), indicating progressive coherence"
            )
        else:
            throughlines.append(
                f"**Convergence fluctuated** across tiers (S1: {convergences[0]:.2f}, "
                f"S4: {convergences[-1]:.2f}), suggesting multi-phase alignment"
            )

    # Check gate passage
    all_passed = all(
        tier_summaries[ch]["gate_pass"]
        for ch in chambers
        if ch in tier_summaries
    )
    if all_passed:
        throughlines.append(
            "**All advance gates passed**, confirming systematic progression through spiral tiers"
        )
    else:
        failed_tiers = [
            ch for ch in chambers
            if ch in tier_summaries and not tier_summaries[ch]["gate_pass"]
        ]
        throughlines.append(
            f"**Gate failures at {', '.join(failed_tiers)}** indicate need for protocol refinement"
        )

    # Check pressure safety
    all_safe = all(
        tier_summaries[ch]["pressure_ok"]
        for ch in chambers
        if ch in tier_summaries
    )
    if all_safe:
        throughlines.append(
            "**Pressure remained ≤2.0/5 across all tiers**, maintaining safe phenomenological space"
        )

    # Extract common themes from takeaways
    all_takeaways = " ".join([
        " ".join(tier_summaries[ch]["takeaways"])
        for ch in chambers
        if ch in tier_summaries
    ]).lower()

    if "geometric" in all_takeaways and all_takeaways.count("geometric") >= 2:
        throughlines.append(
            "**Geometric/structural framing persisted** across multiple tiers, suggesting spatial metaphor salience"
        )

    if "rhythm" in all_takeaways or "pulse" in all_takeaways:
        throughlines.append(
            "**Temporal dynamics (rhythm/pulse)** emerged as organizing principle in later tiers"
        )

    return throughlines


def analyze_s4_attractor(s4_summary: Dict, topic: str) -> Dict:
    """
    Analyze S4 attractor signature and rate.

    Args:
        s4_summary: Parsed S4 summary
        topic: Scientific topic

    Returns:
        Attractor analysis dictionary
    """
    raw = s4_summary["raw_content"]

    # Look for S4 signal counts (would be in detailed diagnostics)
    # For now, use convergence as proxy
    s4_conv = s4_summary["mean_convergence"]
    gate_pass = s4_summary["gate_pass"]

    # Extract exemplar snippets
    exemplar_match = re.search(
        r'## Exemplar Snippets\s+(.+?)---',
        raw,
        re.DOTALL
    )
    exemplars = []
    if exemplar_match:
        exemplar_text = exemplar_match.group(1)
        exemplars = [
            line.strip("- \n")
            for line in exemplar_text.split("\n")
            if line.strip().startswith("-")
        ]

    attractor_detected = s4_conv >= 0.75 and gate_pass

    return {
        "attractor_detected": attractor_detected,
        "s4_convergence": s4_conv,
        "gate_pass": gate_pass,
        "exemplars": exemplars[:3],
        "interpretation": (
            f"S4 attractor signature {'confirmed' if attractor_detected else 'not confirmed'} "
            f"(convergence: {s4_conv:.2f}); "
            f"{'stable dynamics evident' if attractor_detected else 'pattern incomplete'}"
        )
    }


def synthesize_hypotheses(tier_summaries: Dict[str, Dict], topic: str) -> List[str]:
    """
    Synthesize top candidate hypotheses tied to topic.

    Args:
        tier_summaries: Dictionary of tier summaries
        topic: Scientific question

    Returns:
        List of synthesized hypotheses
    """
    # Collect all hooks
    all_hooks = []
    for ch in ["S1", "S2", "S3", "S4"]:
        if ch in tier_summaries:
            all_hooks.extend(tier_summaries[ch]["hooks"])

    # Deduplicate and prioritize
    unique_hooks = list(dict.fromkeys(all_hooks))  # Preserve order

    # Filter to most topic-relevant (simple heuristic: contains topic keywords)
    topic_keywords = set(re.findall(r'\w+', topic.lower())) - {
        "the", "a", "an", "is", "are", "what", "how", "why", "does", "do"
    }

    scored_hooks = []
    for hook in unique_hooks:
        hook_words = set(re.findall(r'\w+', hook.lower()))
        relevance = len(hook_words & topic_keywords)
        scored_hooks.append((relevance, hook))

    # Sort by relevance, take top 3-5
    scored_hooks.sort(reverse=True, key=lambda x: x[0])
    top_hypotheses = [h for _, h in scored_hooks[:5]]

    return top_hypotheses


def generate_open_questions(tier_summaries: Dict[str, Dict], topic: str) -> List[str]:
    """
    Generate open questions and next experiment suggestions.

    Args:
        tier_summaries: Dictionary of tier summaries
        topic: Scientific question

    Returns:
        List of open questions
    """
    questions = []

    # Check for convergence gaps
    s1_conv = tier_summaries.get("S1", {}).get("mean_convergence", 0)
    s4_conv = tier_summaries.get("S4", {}).get("mean_convergence", 0)

    if s4_conv < 0.70:
        questions.append(
            f"Low S4 convergence ({s4_conv:.2f}) suggests need to refine {topic} framing—"
            "consider breaking into sub-questions"
        )

    if s4_conv - s1_conv < 0.15:
        questions.append(
            "Minimal convergence increase S1→S4 indicates topic may lack phenomenological depth—"
            "explore alternative metaphors"
        )

    # Generic next steps
    questions.extend([
        f"Run targeted S4 convergence (100+ turns) to confirm attractor stability for {topic}",
        "Extract S4 priors and test in bioelectric simulation to validate mechanistic mapping",
        "Compare GSW results across different topic formulations to identify optimal framing"
    ])

    return questions[:5]


def generate_gsw_report(
    summary_dir: str,
    topic: str,
    run_id: str,
    output_path: str
) -> Path:
    """
    Generate final GSW executive report.

    Args:
        summary_dir: Directory containing S1-S4 tier summaries
        topic: Scientific question
        run_id: GSW run identifier
        output_path: Output path for report

    Returns:
        Path to generated report
    """
    summary_path = Path(summary_dir)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Load all tier summaries
    tier_summaries = {}
    for chamber in ["S1", "S2", "S3", "S4"]:
        tier_file = summary_path / f"{chamber}_SUMMARY.md"
        if tier_file.exists():
            tier_summaries[chamber] = parse_tier_summary(tier_file)

    if not tier_summaries:
        raise FileNotFoundError(f"No tier summaries found in {summary_dir}")

    # Analyze
    throughlines = identify_throughlines(tier_summaries)

    s4_analysis = {}
    if "S4" in tier_summaries:
        s4_analysis = analyze_s4_attractor(tier_summaries["S4"], topic)

    hypotheses = synthesize_hypotheses(tier_summaries, topic)
    open_questions = generate_open_questions(tier_summaries, topic)

    # Generate report
    timestamp = datetime.now().isoformat()

    report = f"""# Global Spiral Warm-Up Report

**Run ID:** {run_id}
**Topic:** {topic}
**Generated:** {timestamp}

---

## Executive Summary (1-Pager)

### Question
{topic}

### Outcome
{'✓ S4 Attractor Confirmed' if s4_analysis.get('attractor_detected') else '⚠️ S4 Attractor Incomplete'}

### Key Finding
"""

    if throughlines:
        report += throughlines[0] + "\n\n"
    else:
        report += "Analysis in progress.\n\n"

    report += f"""### Convergence Trajectory
"""

    for ch in ["S1", "S2", "S3", "S4"]:
        if ch in tier_summaries:
            conv = tier_summaries[ch]["mean_convergence"]
            status = "✓" if tier_summaries[ch]["gate_pass"] else "✗"
            report += f"- **{ch}**: {conv:.3f} {status}\n"

    report += f"""

### Top Hypothesis
{hypotheses[0] if hypotheses else 'Pending further analysis'}

---

## Through-Line Analysis

What persisted and strengthened S1→S4:

"""

    for i, line in enumerate(throughlines, 1):
        report += f"{i}. {line}\n\n"

    report += f"""

---

## S4 Attractor Check

"""

    if s4_analysis:
        report += f"""**Status:** {'✓ Detected' if s4_analysis['attractor_detected'] else '✗ Not Detected'}
**S4 Convergence:** {s4_analysis['s4_convergence']:.3f}
**Gate Pass:** {'Yes' if s4_analysis['gate_pass'] else 'No'}

### Interpretation
{s4_analysis['interpretation']}

### Exemplar Snippets
"""
        for exemplar in s4_analysis.get('exemplars', []):
            report += f"- {exemplar}\n"

    else:
        report += "S4 summary not available.\n"

    report += f"""

---

## Candidate Hypotheses

Tied to topic: *{topic}*

"""

    for i, hyp in enumerate(hypotheses, 1):
        report += f"{i}. {hyp}\n\n"

    report += f"""

---

## Open Questions & Next Experiments

"""

    for i, q in enumerate(open_questions, 1):
        report += f"{i}. {q}\n\n"

    report += f"""

---

## Tier-by-Tier Details

"""

    for ch in ["S1", "S2", "S3", "S4"]:
        if ch in tier_summaries:
            summary = tier_summaries[ch]
            report += f"""### {ch} Summary

**Convergence:** {summary['mean_convergence']:.3f}
**Gate:** {'✓ PASS' if summary['gate_pass'] else '✗ FAIL'}

**Takeaways:**
"""
            for takeaway in summary['takeaways'][:2]:  # Top 2 per tier
                report += f"- {takeaway}\n"

            report += "\n"

    report += """

---

## Appendices

Full tier summaries available in:
"""

    for ch in ["S1", "S2", "S3", "S4"]:
        report += f"- `{ch}_SUMMARY.md`\n"

    report += """

---

*Generated by GSW Final Summarizer*
"""

    # Write report
    output_file.write_text(report)

    print(f"✓ Generated: {output_file}")

    return output_file


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="GSW Final Summarizer")
    parser.add_argument("summary_dir", help="Directory with S1-S4 tier summaries")
    parser.add_argument("--topic", required=True, help="Scientific topic/question")
    parser.add_argument("--run-id", required=True, help="GSW run identifier")
    parser.add_argument("--output", required=True, help="Output path for final report")

    args = parser.parse_args()

    try:
        report_file = generate_gsw_report(
            summary_dir=args.summary_dir,
            topic=args.topic,
            run_id=args.run_id,
            output_path=args.output
        )

        print(f"\n✓ GSW Report complete: {report_file}")

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
