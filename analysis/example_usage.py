#!/usr/bin/env python3
"""
Example usage of IRIS Gate analysis modules.

Demonstrates programmatic access to key functionality.
"""

from pathlib import Path
from data_loader import load_session
from concept_extractor import ConceptExtractor

# NOTE: Uncomment these imports after installing requirements.txt
# from convergence_analyzer import ConvergenceAnalyzer
# from visualizer import ConvergenceVisualizer
# from report_generator import ReportGenerator


def example_basic_loading():
    """Example 1: Load and explore checkpoint data."""
    print("="*60)
    print("Example 1: Basic Data Loading")
    print("="*60)

    # Load session
    session_dir = "/Users/vaquez/iris-gate/iris_vault/sessions/MASS_COHERENCE_20260109_041127"
    loader = load_session(session_dir)

    # Get metadata
    probe_ids = loader.get_probe_ids()
    architectures = loader.get_architectures()

    print(f"Found {len(probe_ids)} probes: {', '.join(probe_ids)}")
    print(f"Architectures: {', '.join(architectures)}")

    # Load specific probe history
    probe_history = loader.load_probe_history("PROBE_1")
    print(f"\nPROBE_1 has {len(probe_history)} iterations")

    # Access specific responses
    first_iter_responses = probe_history[1]
    print(f"Iteration 1 has {len(first_iter_responses)} responses:")
    for response in first_iter_responses:
        print(f"  - {response.architecture}: {response.word_count} words")


def example_concept_extraction():
    """Example 2: Extract physics concepts from responses."""
    print("\n" + "="*60)
    print("Example 2: Concept Extraction")
    print("="*60)

    # Load data
    session_dir = "/Users/vaquez/iris-gate/iris_vault/sessions/MASS_COHERENCE_20260109_041127"
    loader = load_session(session_dir)
    probe_history = loader.load_probe_history("PROBE_1")

    # Get Claude's first response
    claude_response = next(r for r in probe_history[1] if r.architecture == "claude")

    # Extract concepts
    extractor = ConceptExtractor()
    profile = extractor.extract_profile(claude_response)

    print(f"\nClaude's Response on PROBE_1:")
    print(f"  Citations: {', '.join(profile.citations)}")
    print(f"  Frameworks: {', '.join(set(profile.frameworks))}")
    print(f"  Top keywords: {', '.join(list(set(profile.keywords))[:10])}")
    print(f"  Equations found: {len(profile.equations)}")


def example_convergence_analysis():
    """Example 3: Analyze convergence (requires ML dependencies)."""
    print("\n" + "="*60)
    print("Example 3: Convergence Analysis")
    print("="*60)

    try:
        from convergence_analyzer import ConvergenceAnalyzer

        # Load data
        session_dir = "/Users/vaquez/iris-gate/iris_vault/sessions/MASS_COHERENCE_20260109_041127"
        loader = load_session(session_dir)
        probe_history = loader.load_probe_history("PROBE_1")

        # Initialize analyzer
        print("Initializing analyzer (downloading model if needed)...")
        analyzer = ConvergenceAnalyzer()

        # Analyze single iteration
        print("Computing similarities for iteration 1...")
        responses = probe_history[1]
        metrics = analyzer.analyze_probe_iteration("PROBE_1", 1, responses)

        print(f"\nPROBE_1 Iteration 1:")
        print(f"  Mean similarity: {metrics.mean_similarity:.3f}")
        print(f"  Convergence score: {metrics.convergence_score:.3f}")
        print(f"  Min similarity: {metrics.min_similarity:.3f}")

        # Find most divergent pair
        n = len(metrics.architecture_names)
        min_sim = 1.0
        min_pair = None
        for i in range(n):
            for j in range(i+1, n):
                sim = metrics.similarity_matrix[i, j]
                if sim < min_sim:
                    min_sim = sim
                    min_pair = (metrics.architecture_names[i], metrics.architecture_names[j])

        if min_pair:
            print(f"  Most divergent pair: {min_pair[0]} vs {min_pair[1]} ({min_sim:.3f})")

        # Analyze evolution
        print("\nAnalyzing evolution across iterations...")
        all_metrics = analyzer.analyze_probe_evolution(probe_history)

        print(f"Convergence trajectory:")
        for metric in all_metrics:
            print(f"  Iteration {metric.iteration}: {metric.convergence_score:.3f}")

    except ImportError:
        print("Convergence analysis requires ML dependencies:")
        print("  pip install sentence-transformers torch")


def example_visualization():
    """Example 4: Generate visualizations (requires ML dependencies)."""
    print("\n" + "="*60)
    print("Example 4: Visualization")
    print("="*60)

    try:
        from convergence_analyzer import ConvergenceAnalyzer
        from visualizer import ConvergenceVisualizer

        # Load data
        session_dir = "/Users/vaquez/iris-gate/iris_vault/sessions/MASS_COHERENCE_20260109_041127"
        loader = load_session(session_dir)
        probe_history = loader.load_probe_history("PROBE_1")

        # Analyze
        analyzer = ConvergenceAnalyzer()
        metrics_list = analyzer.analyze_probe_evolution(probe_history)

        # Visualize
        output_dir = Path("example_output")
        visualizer = ConvergenceVisualizer(output_dir=output_dir)

        # Create trajectory plot
        trajectory = analyzer.compute_convergence_trajectory(metrics_list)
        fig = visualizer.plot_convergence_trajectory(
            trajectory,
            "PROBE_1",
            save_as="example_trajectory.png"
        )

        print(f"Trajectory plot saved to: {output_dir}/example_trajectory.png")

        # Create similarity matrix for final iteration
        final_metric = metrics_list[-1]
        fig = visualizer.plot_similarity_matrix(
            final_metric,
            save_as="example_similarity.png"
        )

        print(f"Similarity matrix saved to: {output_dir}/example_similarity.png")

    except ImportError:
        print("Visualization requires ML dependencies:")
        print("  pip install sentence-transformers torch matplotlib seaborn")


def example_search():
    """Example 5: Search for specific concepts."""
    print("\n" + "="*60)
    print("Example 5: Concept Search")
    print("="*60)

    # Load data
    session_dir = "/Users/vaquez/iris-gate/iris_vault/sessions/MASS_COHERENCE_20260109_041127"
    loader = load_session(session_dir)
    checkpoints = loader.load_all_checkpoints()

    # Search for Verlinde
    query = "Verlinde"
    matches = []

    for cp in checkpoints:
        for response in cp.probe_responses:
            if query.lower() in response.response.lower():
                matches.append(response)

    print(f"Found {len(matches)} responses mentioning '{query}'")

    # Show first match with context
    if matches:
        first_match = matches[0]
        print(f"\nFirst match:")
        print(f"  Probe: {first_match.probe_id}")
        print(f"  Architecture: {first_match.architecture}")
        print(f"  Iteration: {first_match.iteration}")

        # Extract context
        text = first_match.response
        idx = text.lower().find(query.lower())
        if idx >= 0:
            start = max(0, idx - 150)
            end = min(len(text), idx + 150)
            context = text[start:end]
            if start > 0:
                context = "..." + context
            if end < len(text):
                context = context + "..."
            print(f"\n  Context:\n  {context}")


def example_comparison():
    """Example 6: Compare two architectures."""
    print("\n" + "="*60)
    print("Example 6: Architecture Comparison")
    print("="*60)

    # Load data
    session_dir = "/Users/vaquez/iris-gate/iris_vault/sessions/MASS_COHERENCE_20260109_041127"
    loader = load_session(session_dir)
    probe_history = loader.load_probe_history("PROBE_1")

    # Compare Claude vs GPT
    arch1, arch2 = "claude", "gpt"
    extractor = ConceptExtractor()

    print(f"Comparing {arch1} vs {arch2} on PROBE_1:\n")

    for iteration in sorted(probe_history.keys())[:3]:  # First 3 iterations
        responses = probe_history[iteration]

        resp1 = next((r for r in responses if r.architecture == arch1), None)
        resp2 = next((r for r in responses if r.architecture == arch2), None)

        if resp1 and resp2:
            profile1 = extractor.extract_profile(resp1)
            profile2 = extractor.extract_profile(resp2)

            citations1 = set(profile1.citations)
            citations2 = set(profile2.citations)

            common = citations1 & citations2
            unique1 = citations1 - citations2
            unique2 = citations2 - citations1

            print(f"Iteration {iteration}:")
            print(f"  {arch1}: {resp1.word_count} words, {len(citations1)} citations")
            print(f"  {arch2}: {resp2.word_count} words, {len(citations2)} citations")

            if common:
                print(f"  Common: {', '.join(sorted(common))}")
            if unique1:
                print(f"  Only {arch1}: {', '.join(sorted(unique1))}")
            if unique2:
                print(f"  Only {arch2}: {', '.join(sorted(unique2))}")
            print()


if __name__ == "__main__":
    # Run all examples
    print("IRIS Gate Analysis - Example Usage\n")

    example_basic_loading()
    example_concept_extraction()
    example_search()
    example_comparison()

    # These require ML dependencies
    example_convergence_analysis()
    example_visualization()

    print("\n" + "="*60)
    print("Examples Complete")
    print("="*60)
