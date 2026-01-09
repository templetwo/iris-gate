#!/usr/bin/env python3
"""
IRIS Gate Convergence Analysis CLI

Main entry point for analyzing convergence data, generating visualizations,
and creating comprehensive reports.

Usage:
    python analyze_convergence.py <session_dir> [options]

Examples:
    # Full analysis with all visualizations
    python analyze_convergence.py iris_vault/sessions/MASS_COHERENCE_20260109_041127

    # Analyze specific probe
    python analyze_convergence.py <session_dir> --probe PROBE_5

    # Quick analysis without embeddings
    python analyze_convergence.py <session_dir> --skip-embeddings

    # Search for physics concepts
    python analyze_convergence.py <session_dir> --search "Verlinde"
"""

import argparse
import logging
from pathlib import Path
import sys
from collections import defaultdict

from data_loader import load_session, ProbeResponse
from convergence_analyzer import ConvergenceAnalyzer
from concept_extractor import ConceptExtractor, analyze_concepts_batch
from visualizer import ConvergenceVisualizer
from report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_full_session(
    session_dir: str,
    output_dir: str,
    skip_embeddings: bool = False,
    probe_filter: str = None
):
    """
    Run complete analysis pipeline.

    Args:
        session_dir: Path to session directory
        output_dir: Path to output directory
        skip_embeddings: If True, skip semantic similarity analysis
        probe_filter: If provided, only analyze this probe
    """
    logger.info(f"Loading session data from: {session_dir}")
    loader = load_session(session_dir)

    probe_ids = loader.get_probe_ids()
    if probe_filter:
        if probe_filter in probe_ids:
            probe_ids = [probe_filter]
        else:
            logger.error(f"Probe {probe_filter} not found. Available: {probe_ids}")
            return

    logger.info(f"Probes to analyze: {probe_ids}")
    logger.info(f"Architectures: {loader.get_architectures()}")

    # Initialize components
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    viz_dir = output_path / "figures"
    cache_dir = output_path / "cache"

    visualizer = ConvergenceVisualizer(output_dir=viz_dir)
    report_gen = ReportGenerator(output_dir=output_path)
    concept_extractor = ConceptExtractor()

    # Storage for results
    all_metrics = {}
    all_profiles = {}
    divergent_probes = {}
    response_lengths = defaultdict(lambda: defaultdict(list))

    # Analyze each probe
    for probe_id in probe_ids:
        logger.info(f"\n{'='*60}")
        logger.info(f"Analyzing {probe_id}")
        logger.info(f"{'='*60}")

        # Load probe history
        probe_history = loader.load_probe_history(probe_id)

        # Extract concepts
        logger.info("Extracting physics concepts...")
        all_responses = []
        for iter_responses in probe_history.values():
            all_responses.extend(iter_responses)

        profiles = analyze_concepts_batch(all_responses, concept_extractor)
        all_profiles[probe_id] = profiles

        # Track response lengths
        for response in all_responses:
            response_lengths[response.architecture][response.iteration].append(
                response.response_length
            )

        # Convergence analysis
        if not skip_embeddings:
            logger.info("Computing semantic embeddings and convergence metrics...")
            analyzer = ConvergenceAnalyzer(cache_dir=cache_dir)

            metrics = analyzer.analyze_probe_evolution(probe_history)
            all_metrics[probe_id] = metrics

            # Detect divergence
            divergent = analyzer.detect_divergence(metrics)
            divergent_probes[probe_id] = divergent

            if divergent:
                logger.warning(f"Divergence detected at iterations: {divergent}")

            # Generate visualizations
            logger.info("Creating visualizations...")

            # Trajectory plot
            trajectory = analyzer.compute_convergence_trajectory(metrics)
            visualizer.plot_convergence_trajectory(
                trajectory,
                probe_id,
                highlight_divergence=divergent
            )

            # Similarity matrix for final iteration
            final_metric = metrics[-1]
            visualizer.plot_similarity_matrix(final_metric)

        else:
            logger.info("Skipping embeddings (--skip-embeddings)")

    # Cross-probe visualizations
    if not skip_embeddings and not probe_filter:
        logger.info("\n" + "="*60)
        logger.info("Generating cross-probe visualizations")
        logger.info("="*60)

        # Probe comparison heatmap
        visualizer.plot_probe_comparison_heatmap(all_metrics)

        # Response length evolution
        visualizer.plot_response_length_evolution(dict(response_lengths))

        # Summary dashboard
        visualizer.create_summary_dashboard(all_metrics)

    # Concept analysis visualizations
    logger.info("\n" + "="*60)
    logger.info("Analyzing physics concepts")
    logger.info("="*60)

    all_profiles_flat = [p for profiles in all_profiles.values() for p in profiles]

    # Citation network
    citation_network = concept_extractor.build_citation_network(all_profiles_flat)
    if citation_network:
        visualizer.plot_citation_network(citation_network)

    # Framework usage
    framework_usage = concept_extractor.compute_framework_usage(all_profiles_flat)
    if framework_usage:
        visualizer.plot_framework_usage(framework_usage)

    # Find novel proposals
    all_responses = [r for profiles in all_profiles.values()
                     for p in profiles
                     for cp in loader.load_all_checkpoints()
                     for r in cp.probe_responses
                     if (r.probe_id, r.iteration, r.architecture) == p.response_id]

    if all_responses:
        novel_proposals = concept_extractor.find_novel_proposals(all_responses)
        if novel_proposals:
            logger.info(f"\nFound {len(novel_proposals)} novel physics proposals")

    # Generate report
    if not skip_embeddings:
        logger.info("\n" + "="*60)
        logger.info("Generating comprehensive report")
        logger.info("="*60)

        report_path = report_gen.generate_full_report(
            loader,
            all_metrics,
            all_profiles,
            divergent_probes
        )

        logger.info(f"\nAnalysis complete!")
        logger.info(f"Report: {report_path}")
        logger.info(f"Figures: {viz_dir}")


def search_responses(session_dir: str, query: str):
    """
    Search responses for specific physics concepts.

    Args:
        session_dir: Path to session directory
        query: Search query (case-insensitive)
    """
    loader = load_session(session_dir)
    checkpoints = loader.load_all_checkpoints()

    matches = []
    query_lower = query.lower()

    for cp in checkpoints:
        for response in cp.probe_responses:
            if query_lower in response.response.lower():
                matches.append(response)

    logger.info(f"\nFound {len(matches)} responses mentioning '{query}'")

    for response in matches:
        print(f"\n{'='*60}")
        print(f"Probe: {response.probe_id}, Iteration: {response.iteration}")
        print(f"Architecture: {response.architecture}")
        print(f"{'='*60}")

        # Extract context around query
        text = response.response
        idx = text.lower().find(query_lower)
        if idx >= 0:
            start = max(0, idx - 200)
            end = min(len(text), idx + 200)
            context = text[start:end]
            if start > 0:
                context = "..." + context
            if end < len(text):
                context = context + "..."
            print(context)


def compare_architectures(session_dir: str, probe_id: str, arch1: str, arch2: str):
    """
    Compare specific architectures on a probe.

    Args:
        session_dir: Path to session directory
        probe_id: Probe to compare
        arch1: First architecture
        arch2: Second architecture
    """
    loader = load_session(session_dir)
    probe_history = loader.load_probe_history(probe_id)

    if not probe_history:
        logger.error(f"Probe {probe_id} not found")
        return

    print(f"\n{'='*60}")
    print(f"Comparing {arch1} vs {arch2} on {probe_id}")
    print(f"{'='*60}\n")

    for iteration, responses in sorted(probe_history.items()):
        resp1 = next((r for r in responses if r.architecture == arch1), None)
        resp2 = next((r for r in responses if r.architecture == arch2), None)

        if resp1 and resp2:
            print(f"\nIteration {iteration}:")
            print(f"  {arch1}: {resp1.word_count} words")
            print(f"  {arch2}: {resp2.word_count} words")

            # Extract concepts
            extractor = ConceptExtractor()
            profile1 = extractor.extract_profile(resp1)
            profile2 = extractor.extract_profile(resp2)

            # Compare citations
            citations1 = set(profile1.citations)
            citations2 = set(profile2.citations)

            common = citations1 & citations2
            unique1 = citations1 - citations2
            unique2 = citations2 - citations1

            if common:
                print(f"  Common citations: {', '.join(common)}")
            if unique1:
                print(f"  Unique to {arch1}: {', '.join(unique1)}")
            if unique2:
                print(f"  Unique to {arch2}: {', '.join(unique2)}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze IRIS Gate convergence data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "session_dir",
        help="Path to session directory containing checkpoints"
    )

    parser.add_argument(
        "-o", "--output",
        default="analysis_output",
        help="Output directory for results (default: analysis_output)"
    )

    parser.add_argument(
        "--probe",
        help="Analyze only specific probe (e.g., PROBE_1)"
    )

    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Skip semantic embedding analysis (faster, but no similarity metrics)"
    )

    parser.add_argument(
        "--search",
        help="Search responses for specific concept"
    )

    parser.add_argument(
        "--compare",
        nargs=3,
        metavar=("PROBE", "ARCH1", "ARCH2"),
        help="Compare two architectures on a probe"
    )

    args = parser.parse_args()

    # Validate session directory
    if not Path(args.session_dir).exists():
        logger.error(f"Session directory not found: {args.session_dir}")
        sys.exit(1)

    # Execute appropriate command
    if args.search:
        search_responses(args.session_dir, args.search)
    elif args.compare:
        compare_architectures(args.session_dir, args.compare[0], args.compare[1], args.compare[2])
    else:
        analyze_full_session(
            args.session_dir,
            args.output,
            skip_embeddings=args.skip_embeddings,
            probe_filter=args.probe
        )


if __name__ == "__main__":
    main()
