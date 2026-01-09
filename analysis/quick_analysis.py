#!/usr/bin/env python3
"""
Quick analysis without ML dependencies.

Provides basic statistics and concept extraction without semantic embeddings.
Useful for rapid exploration before running full analysis.

Usage:
    python quick_analysis.py <session_dir>
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

from data_loader import load_session
from concept_extractor import ConceptExtractor


def quick_stats(session_dir: str):
    """
    Generate quick statistics without embeddings.

    Args:
        session_dir: Path to session directory
    """
    print("="*60)
    print("IRIS Gate Quick Analysis")
    print("="*60)

    # Load data
    loader = load_session(session_dir)
    checkpoints = loader.load_all_checkpoints()

    print(f"\nSession: {checkpoints[0].session_id if checkpoints else 'Unknown'}")
    print(f"Iterations: {len(checkpoints)}")
    print(f"Architectures: {', '.join(loader.get_architectures())}")
    print(f"Probes: {', '.join(loader.get_probe_ids())}")

    # Response statistics
    total_responses = sum(cp.num_responses for cp in checkpoints)
    print(f"\nTotal responses: {total_responses}")

    # Response lengths by architecture
    print("\n" + "="*60)
    print("Response Length Statistics")
    print("="*60)

    arch_lengths = defaultdict(list)
    for cp in checkpoints:
        for response in cp.probe_responses:
            arch_lengths[response.architecture].append(response.response_length)

    for arch in sorted(arch_lengths.keys()):
        lengths = arch_lengths[arch]
        avg_len = sum(lengths) / len(lengths)
        print(f"{arch:12s}: {avg_len:8.0f} chars avg ({len(lengths)} responses)")

    # Evolution over iterations
    print("\n" + "="*60)
    print("Response Growth Over Iterations")
    print("="*60)

    for cp in checkpoints:
        total_chars = sum(r.response_length for r in cp.probe_responses)
        avg_chars = total_chars / len(cp.probe_responses) if cp.probe_responses else 0
        print(f"Iteration {cp.iteration:2d}: {avg_chars:8.0f} chars avg")

    # Concept extraction
    print("\n" + "="*60)
    print("Physics Concept Analysis")
    print("="*60)

    extractor = ConceptExtractor()

    all_citations = Counter()
    all_frameworks = Counter()
    all_keywords = Counter()

    for cp in checkpoints:
        for response in cp.probe_responses:
            profile = extractor.extract_profile(response)
            all_citations.update(profile.citations)
            all_frameworks.update(profile.frameworks)
            all_keywords.update(profile.keywords)

    print("\nTop Citations:")
    for cite, count in all_citations.most_common(10):
        print(f"  {cite:20s}: {count:3d} mentions")

    print("\nTop Frameworks:")
    for framework, count in all_frameworks.most_common(10):
        print(f"  {framework:30s}: {count:3d} mentions")

    print("\nTop Keywords:")
    for keyword, count in all_keywords.most_common(15):
        print(f"  {keyword:20s}: {count:3d} mentions")

    # Probe-specific analysis
    print("\n" + "="*60)
    print("Probe-Specific Statistics")
    print("="*60)

    for probe_id in loader.get_probe_ids():
        probe_history = loader.load_probe_history(probe_id)

        print(f"\n{probe_id}:")
        print(f"  Iterations: {len(probe_history)}")

        # Get final iteration
        final_iter = max(probe_history.keys())
        final_responses = probe_history[final_iter]

        print(f"  Final iteration responses: {len(final_responses)}")

        # Response length variance
        lengths = [r.response_length for r in final_responses]
        if lengths:
            avg = sum(lengths) / len(lengths)
            variance = sum((l - avg)**2 for l in lengths) / len(lengths)
            std = variance ** 0.5
            print(f"  Final length avg: {avg:.0f} chars (std: {std:.0f})")

        # Citations per architecture
        arch_citations = defaultdict(set)
        for response in final_responses:
            profile = extractor.extract_profile(response)
            arch_citations[response.architecture].update(profile.citations)

        # Find common citations
        if len(arch_citations) > 1:
            common_citations = set.intersection(*arch_citations.values())
            if common_citations:
                print(f"  Common citations: {', '.join(common_citations)}")

    # Novel proposals
    print("\n" + "="*60)
    print("Novel Physics Proposals")
    print("="*60)

    all_responses = []
    for cp in checkpoints:
        all_responses.extend(cp.probe_responses)

    proposals = extractor.find_novel_proposals(all_responses, min_length=150, max_count=5)

    for i, (arch, probe, text) in enumerate(proposals, 1):
        print(f"\n{i}. {arch} on {probe}:")
        # Truncate long proposals
        if len(text) > 300:
            text = text[:300] + "..."
        print(f"   {text}")

    print("\n" + "="*60)
    print("Analysis Complete")
    print("="*60)
    print("\nFor full semantic similarity analysis, run:")
    print(f"  python analyze_convergence.py {session_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python quick_analysis.py <session_dir>")
        sys.exit(1)

    session_dir = sys.argv[1]

    if not Path(session_dir).exists():
        print(f"Error: Session directory not found: {session_dir}")
        sys.exit(1)

    quick_stats(session_dir)
