"""
Report generation for convergence analysis.

Generates comprehensive markdown reports with statistics,
findings, and embedded figures.
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

from data_loader import DataLoader, CheckpointData
from convergence_analyzer import ConvergenceMetrics, ConvergenceAnalyzer
from concept_extractor import ConceptProfile, ConceptExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generate comprehensive analysis reports.

    Creates markdown reports with:
    - Executive summary
    - Probe-by-probe analysis
    - Architecture comparison
    - Key findings
    - Embedded visualizations
    """

    def __init__(self, output_dir: Path):
        """
        Initialize report generator.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_probe_report(
        self,
        probe_id: str,
        metrics: List[ConvergenceMetrics],
        profiles: List[ConceptProfile],
        divergent_iterations: List[int]
    ) -> str:
        """
        Generate detailed report for a single probe.

        Args:
            probe_id: Probe identifier
            metrics: List of convergence metrics
            profiles: List of concept profiles
            divergent_iterations: Iterations flagged as divergent

        Returns:
            Markdown report string
        """
        report = []

        report.append(f"# {probe_id} Analysis\n")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("---\n")

        # Summary statistics
        final_metric = metrics[-1]
        report.append("## Summary\n")
        report.append(f"- **Total Iterations**: {len(metrics)}\n")
        report.append(f"- **Final Convergence Score**: {final_metric.convergence_score:.3f}\n")
        report.append(f"- **Final Mean Similarity**: {final_metric.mean_similarity:.3f}\n")
        report.append(f"- **Final Std Dev**: {final_metric.std_similarity:.3f}\n")
        report.append(f"- **Divergent Iterations**: {divergent_iterations if divergent_iterations else 'None'}\n")
        report.append("\n")

        # Convergence assessment
        report.append("## Convergence Assessment\n")
        if final_metric.convergence_score > 0.7:
            assessment = "STRONG CONVERGENCE"
        elif final_metric.convergence_score > 0.5:
            assessment = "MODERATE CONVERGENCE"
        elif final_metric.convergence_score > 0.3:
            assessment = "WEAK CONVERGENCE"
        else:
            assessment = "DIVERGENCE"

        report.append(f"**Status**: {assessment}\n\n")

        # Trajectory analysis
        report.append("## Convergence Trajectory\n")
        initial_metric = metrics[0]
        change = final_metric.convergence_score - initial_metric.convergence_score

        if change > 0.1:
            trend = "INCREASING"
        elif change < -0.1:
            trend = "DECREASING"
        else:
            trend = "STABLE"

        report.append(f"- **Initial Score**: {initial_metric.convergence_score:.3f}\n")
        report.append(f"- **Final Score**: {final_metric.convergence_score:.3f}\n")
        report.append(f"- **Change**: {change:+.3f}\n")
        report.append(f"- **Trend**: {trend}\n\n")

        # Architecture similarity matrix
        report.append("## Final Architecture Similarity\n")
        report.append("```\n")
        report.append("         " + "  ".join(f"{a:8s}" for a in final_metric.architecture_names) + "\n")
        for i, arch1 in enumerate(final_metric.architecture_names):
            row = f"{arch1:8s} "
            for j in range(len(final_metric.architecture_names)):
                row += f"{final_metric.similarity_matrix[i, j]:8.3f}  "
            report.append(row + "\n")
        report.append("```\n\n")

        # Concept analysis
        if profiles:
            report.append("## Concept Analysis\n")

            # Citations
            all_citations = []
            for profile in profiles:
                all_citations.extend(profile.citations)

            if all_citations:
                from collections import Counter
                citation_counts = Counter(all_citations)
                report.append("### Most Cited Researchers/Frameworks\n")
                for cite, count in citation_counts.most_common(10):
                    report.append(f"- {cite}: {count} mentions\n")
                report.append("\n")

            # Frameworks
            all_frameworks = []
            for profile in profiles:
                all_frameworks.extend(profile.frameworks)

            if all_frameworks:
                from collections import Counter
                framework_counts = Counter(all_frameworks)
                report.append("### Most Used Frameworks\n")
                for framework, count in framework_counts.most_common(10):
                    report.append(f"- {framework}: {count} mentions\n")
                report.append("\n")

        # Key findings
        report.append("## Key Findings\n")

        if final_metric.min_similarity < 0.3:
            report.append("- **ALERT**: Some architecture pairs show very low similarity (< 0.3)\n")
            # Find the most divergent pair
            min_idx = None
            min_val = 1.0
            n = len(final_metric.architecture_names)
            for i in range(n):
                for j in range(i+1, n):
                    if final_metric.similarity_matrix[i, j] < min_val:
                        min_val = final_metric.similarity_matrix[i, j]
                        min_idx = (i, j)
            if min_idx:
                arch1 = final_metric.architecture_names[min_idx[0]]
                arch2 = final_metric.architecture_names[min_idx[1]]
                report.append(f"  - Most divergent pair: {arch1} vs {arch2} (similarity: {min_val:.3f})\n")

        if trend == "DECREASING":
            report.append("- **ALERT**: Convergence score decreased over iterations\n")

        if divergent_iterations:
            report.append(f"- **ALERT**: Divergence detected at iterations: {divergent_iterations}\n")

        report.append("\n")

        return "".join(report)

    def generate_architecture_comparison(
        self,
        all_metrics: Dict[str, List[ConvergenceMetrics]],
        architectures: List[str]
    ) -> str:
        """
        Generate architecture comparison report.

        Args:
            all_metrics: Dict mapping probe_id -> list of metrics
            architectures: List of architecture names

        Returns:
            Markdown report string
        """
        report = []

        report.append("# Architecture Comparison\n")
        report.append("---\n\n")

        # For each architecture, compute average similarity with others
        arch_scores = {arch: [] for arch in architectures}

        for probe_id, metrics_list in all_metrics.items():
            final_metric = metrics_list[-1]

            for i, arch in enumerate(final_metric.architecture_names):
                # Average similarity with all other architectures
                others = [final_metric.similarity_matrix[i, j]
                         for j in range(len(final_metric.architecture_names))
                         if i != j]
                if others:
                    arch_scores[arch].append(sum(others) / len(others))

        # Compute overall scores
        report.append("## Overall Convergence by Architecture\n")
        report.append("Average similarity with other architectures across all probes:\n\n")

        for arch in architectures:
            if arch_scores[arch]:
                avg_score = sum(arch_scores[arch]) / len(arch_scores[arch])
                report.append(f"- **{arch}**: {avg_score:.3f}\n")

        report.append("\n")

        # Pairwise comparison
        report.append("## Pairwise Architecture Similarity\n")
        report.append("Average similarity across all probes (final iteration):\n\n")

        # Build average similarity matrix
        n = len(architectures)
        avg_similarity = {}

        for probe_id, metrics_list in all_metrics.items():
            final_metric = metrics_list[-1]
            for i in range(n):
                for j in range(i+1, n):
                    arch1 = architectures[i]
                    arch2 = architectures[j]
                    key = (arch1, arch2)

                    # Find indices in this metric
                    if arch1 in final_metric.architecture_names and arch2 in final_metric.architecture_names:
                        idx1 = final_metric.architecture_names.index(arch1)
                        idx2 = final_metric.architecture_names.index(arch2)
                        sim = final_metric.similarity_matrix[idx1, idx2]

                        if key not in avg_similarity:
                            avg_similarity[key] = []
                        avg_similarity[key].append(sim)

        # Print pairs sorted by similarity
        sorted_pairs = sorted(
            avg_similarity.items(),
            key=lambda x: sum(x[1])/len(x[1]),
            reverse=True
        )

        for (arch1, arch2), sims in sorted_pairs:
            avg = sum(sims) / len(sims)
            report.append(f"- **{arch1} vs {arch2}**: {avg:.3f}\n")

        report.append("\n")

        return "".join(report)

    def generate_executive_summary(
        self,
        all_metrics: Dict[str, List[ConvergenceMetrics]],
        total_responses: int,
        architectures: List[str]
    ) -> str:
        """
        Generate executive summary.

        Args:
            all_metrics: Dict mapping probe_id -> list of metrics
            total_responses: Total number of responses analyzed
            architectures: List of architecture names

        Returns:
            Markdown report string
        """
        report = []

        report.append("# IRIS Gate Convergence Analysis\n")
        report.append("## Executive Summary\n")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("---\n\n")

        # Dataset statistics
        report.append("## Dataset Statistics\n")
        report.append(f"- **Total Responses**: {total_responses}\n")
        report.append(f"- **Architectures**: {', '.join(architectures)}\n")
        report.append(f"- **Probes Analyzed**: {len(all_metrics)}\n")

        num_iterations = len(next(iter(all_metrics.values())))
        report.append(f"- **Iterations**: {num_iterations}\n\n")

        # Overall convergence
        report.append("## Overall Convergence\n")

        probe_final_scores = {}
        for probe_id, metrics_list in all_metrics.items():
            probe_final_scores[probe_id] = metrics_list[-1].convergence_score

        avg_convergence = sum(probe_final_scores.values()) / len(probe_final_scores)
        report.append(f"- **Average Final Convergence**: {avg_convergence:.3f}\n\n")

        # Probe rankings
        report.append("## Probe Rankings\n")
        report.append("Ranked by final convergence score:\n\n")

        sorted_probes = sorted(
            probe_final_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for i, (probe_id, score) in enumerate(sorted_probes, 1):
            status = "CONVERGED" if score > 0.6 else "DIVERGED" if score < 0.4 else "MIXED"
            report.append(f"{i}. **{probe_id}**: {score:.3f} ({status})\n")

        report.append("\n")

        # Key findings
        report.append("## Key Findings\n")

        # Find most convergent probe
        most_conv_probe, most_conv_score = max(probe_final_scores.items(), key=lambda x: x[1])
        report.append(f"- **Highest Convergence**: {most_conv_probe} ({most_conv_score:.3f})\n")

        # Find most divergent probe
        most_div_probe, most_div_score = min(probe_final_scores.items(), key=lambda x: x[1])
        report.append(f"- **Lowest Convergence**: {most_div_probe} ({most_div_score:.3f})\n")

        # Check for expected divergence (Probe 5)
        if "PROBE_5" in probe_final_scores:
            probe_5_score = probe_final_scores["PROBE_5"]
            if probe_5_score < 0.4:
                report.append("- **Expected Divergence Confirmed**: PROBE_5 (2.9 nat cage) shows divergence as predicted\n")
            else:
                report.append("- **Unexpected Convergence**: PROBE_5 (2.9 nat cage) shows convergence despite expected divergence\n")

        report.append("\n")

        return "".join(report)

    def generate_full_report(
        self,
        loader: DataLoader,
        all_metrics: Dict[str, List[ConvergenceMetrics]],
        all_profiles: Dict[str, List[ConceptProfile]],
        divergent_probes: Dict[str, List[int]],
        filename: str = "full_report.md"
    ) -> Path:
        """
        Generate comprehensive analysis report.

        Args:
            loader: DataLoader instance
            all_metrics: Dict mapping probe_id -> metrics
            all_profiles: Dict mapping probe_id -> profiles
            divergent_probes: Dict mapping probe_id -> divergent iterations
            filename: Output filename

        Returns:
            Path to saved report
        """
        report = []

        # Executive summary
        total_responses = sum(
            cp.num_responses
            for cp in loader.load_all_checkpoints()
        )
        report.append(self.generate_executive_summary(
            all_metrics,
            total_responses,
            loader.get_architectures()
        ))

        report.append("\n---\n\n")

        # Architecture comparison
        report.append(self.generate_architecture_comparison(
            all_metrics,
            loader.get_architectures()
        ))

        report.append("\n---\n\n")

        # Individual probe reports
        report.append("# Detailed Probe Analysis\n\n")

        for probe_id in sorted(all_metrics.keys()):
            metrics = all_metrics[probe_id]
            profiles = all_profiles.get(probe_id, [])
            divergent = divergent_probes.get(probe_id, [])

            probe_report = self.generate_probe_report(
                probe_id,
                metrics,
                profiles,
                divergent
            )
            report.append(probe_report)
            report.append("\n---\n\n")

        # Save report
        report_path = self.output_dir / filename
        with open(report_path, 'w') as f:
            f.write("".join(report))

        logger.info(f"Report saved to: {report_path}")
        return report_path
