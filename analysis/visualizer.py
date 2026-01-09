"""
Visualization tools for convergence analysis.

Creates publication-ready figures including:
- Convergence heatmaps
- Citation networks
- Response evolution plots
- Divergence detection visualizations
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import networkx as nx
from matplotlib.figure import Figure
import logging

from convergence_analyzer import ConvergenceMetrics
from concept_extractor import ConceptProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set publication style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'


class ConvergenceVisualizer:
    """
    Create visualizations for convergence analysis.

    Generates heatmaps, network graphs, time series, and summary plots.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save figures (if None, won't save)
        """
        self.output_dir = Path(output_dir) if output_dir else None
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_figure(self, fig: Figure, filename: str):
        """Save figure if output_dir is set."""
        if self.output_dir:
            filepath = self.output_dir / filename
            fig.savefig(filepath, bbox_inches='tight', dpi=300)
            logger.info(f"Saved figure: {filepath}")

    def plot_similarity_matrix(
        self,
        metrics: ConvergenceMetrics,
        title: Optional[str] = None,
        save_as: Optional[str] = None
    ) -> Figure:
        """
        Plot similarity matrix heatmap for a single iteration.

        Args:
            metrics: ConvergenceMetrics object
            title: Plot title (auto-generated if None)
            save_as: Filename to save (if None, uses auto name)

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(8, 7))

        if title is None:
            title = f"{metrics.probe_id} - Iteration {metrics.iteration}\n" \
                    f"Mean Similarity: {metrics.mean_similarity:.3f}"

        sns.heatmap(
            metrics.similarity_matrix,
            annot=True,
            fmt='.3f',
            cmap='RdYlGn',
            vmin=0,
            vmax=1,
            square=True,
            xticklabels=metrics.architecture_names,
            yticklabels=metrics.architecture_names,
            cbar_kws={'label': 'Cosine Similarity'},
            ax=ax
        )

        ax.set_title(title, fontsize=12, fontweight='bold')
        plt.tight_layout()

        if save_as:
            self._save_figure(fig, save_as)
        elif self.output_dir:
            filename = f"similarity_{metrics.probe_id}_iter{metrics.iteration}.png"
            self._save_figure(fig, filename)

        return fig

    def plot_convergence_trajectory(
        self,
        trajectory: Dict[str, np.ndarray],
        probe_id: str,
        highlight_divergence: Optional[List[int]] = None,
        save_as: Optional[str] = None
    ) -> Figure:
        """
        Plot convergence metrics over iterations.

        Args:
            trajectory: Dict from compute_convergence_trajectory
            probe_id: Probe identifier
            highlight_divergence: Iterations to highlight as divergent
            save_as: Filename to save

        Returns:
            Matplotlib Figure
        """
        fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

        iterations = trajectory['iterations']
        mean_sim = trajectory['mean_similarity']
        std_sim = trajectory['std_similarity']
        conv_score = trajectory['convergence_score']

        # Plot 1: Mean similarity with error bars
        ax1 = axes[0]
        ax1.plot(iterations, mean_sim, 'o-', linewidth=2, markersize=6, label='Mean Similarity')
        ax1.fill_between(
            iterations,
            mean_sim - std_sim,
            mean_sim + std_sim,
            alpha=0.3,
            label='± Std Dev'
        )

        if highlight_divergence:
            for iter_num in highlight_divergence:
                ax1.axvline(iter_num, color='red', linestyle='--', alpha=0.5)

        ax1.set_ylabel('Similarity', fontsize=11)
        ax1.set_title(f'{probe_id} - Convergence Trajectory', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)

        # Plot 2: Convergence score
        ax2 = axes[1]
        ax2.plot(iterations, conv_score, 's-', linewidth=2, markersize=6, color='green', label='Convergence Score')

        if highlight_divergence:
            for iter_num in highlight_divergence:
                ax2.axvline(iter_num, color='red', linestyle='--', alpha=0.5, label='Divergence' if iter_num == highlight_divergence[0] else '')

        ax2.set_xlabel('Iteration', fontsize=11)
        ax2.set_ylabel('Convergence Score', fontsize=11)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1)

        plt.tight_layout()

        if save_as:
            self._save_figure(fig, save_as)
        elif self.output_dir:
            self._save_figure(fig, f"trajectory_{probe_id}.png")

        return fig

    def plot_probe_comparison_heatmap(
        self,
        probe_metrics: Dict[str, List[ConvergenceMetrics]],
        save_as: Optional[str] = None
    ) -> Figure:
        """
        Create heatmap comparing convergence across probes and iterations.

        Args:
            probe_metrics: Dict mapping probe_id -> list of metrics
            save_as: Filename to save

        Returns:
            Matplotlib Figure
        """
        # Build matrix: rows = probes, cols = iterations
        probe_ids = sorted(probe_metrics.keys())
        max_iterations = max(
            max(m.iteration for m in metrics)
            for metrics in probe_metrics.values()
        )

        convergence_matrix = np.zeros((len(probe_ids), max_iterations))

        for i, probe_id in enumerate(probe_ids):
            for metric in probe_metrics[probe_id]:
                iter_idx = metric.iteration - 1  # 0-indexed
                convergence_matrix[i, iter_idx] = metric.convergence_score

        fig, ax = plt.subplots(figsize=(12, 6))

        sns.heatmap(
            convergence_matrix,
            annot=True,
            fmt='.2f',
            cmap='RdYlGn',
            vmin=0,
            vmax=1,
            yticklabels=probe_ids,
            xticklabels=range(1, max_iterations + 1),
            cbar_kws={'label': 'Convergence Score'},
            ax=ax
        )

        ax.set_xlabel('Iteration', fontsize=11)
        ax.set_ylabel('Probe', fontsize=11)
        ax.set_title('Convergence Across Probes and Iterations', fontsize=12, fontweight='bold')

        plt.tight_layout()

        if save_as:
            self._save_figure(fig, save_as)
        elif self.output_dir:
            self._save_figure(fig, "probe_comparison_heatmap.png")

        return fig

    def plot_response_length_evolution(
        self,
        response_lengths: Dict[str, Dict[int, List[int]]],
        save_as: Optional[str] = None
    ) -> Figure:
        """
        Plot response length evolution by architecture.

        Args:
            response_lengths: Dict[architecture][iteration] -> list of lengths
            save_as: Filename to save

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        for arch, iter_data in response_lengths.items():
            iterations = sorted(iter_data.keys())
            mean_lengths = [np.mean(iter_data[i]) for i in iterations]
            ax.plot(iterations, mean_lengths, 'o-', label=arch, linewidth=2, markersize=5)

        ax.set_xlabel('Iteration', fontsize=11)
        ax.set_ylabel('Mean Response Length (characters)', fontsize=11)
        ax.set_title('Response Length Evolution by Architecture', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_as:
            self._save_figure(fig, save_as)
        elif self.output_dir:
            self._save_figure(fig, "response_length_evolution.png")

        return fig

    def plot_citation_network(
        self,
        citation_network: Dict[str, Dict[str, int]],
        min_edge_weight: int = 2,
        save_as: Optional[str] = None
    ) -> Figure:
        """
        Plot citation co-occurrence network.

        Args:
            citation_network: Dict from build_citation_network
            min_edge_weight: Minimum co-occurrence count to draw edge
            save_as: Filename to save

        Returns:
            Matplotlib Figure
        """
        # Build NetworkX graph
        G = nx.Graph()

        for cite1, connections in citation_network.items():
            for cite2, weight in connections.items():
                if weight >= min_edge_weight:
                    G.add_edge(cite1, cite2, weight=weight)

        if len(G.nodes) == 0:
            logger.warning("No citation network to plot (no edges above threshold)")
            return plt.figure()

        fig, ax = plt.subplots(figsize=(12, 10))

        # Layout
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Draw nodes
        node_sizes = [G.degree(node) * 300 for node in G.nodes]
        nx.draw_networkx_nodes(
            G, pos,
            node_size=node_sizes,
            node_color='lightblue',
            alpha=0.9,
            ax=ax
        )

        # Draw edges
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        nx.draw_networkx_edges(
            G, pos,
            width=[w * 0.5 for w in weights],
            alpha=0.6,
            ax=ax
        )

        # Draw labels
        nx.draw_networkx_labels(
            G, pos,
            font_size=10,
            font_weight='bold',
            ax=ax
        )

        ax.set_title('Physics Citation Co-occurrence Network', fontsize=12, fontweight='bold')
        ax.axis('off')

        plt.tight_layout()

        if save_as:
            self._save_figure(fig, save_as)
        elif self.output_dir:
            self._save_figure(fig, "citation_network.png")

        return fig

    def plot_framework_usage(
        self,
        framework_usage: Dict[str, int],
        top_n: int = 10,
        save_as: Optional[str] = None
    ) -> Figure:
        """
        Plot framework usage bar chart.

        Args:
            framework_usage: Dict from compute_framework_usage
            top_n: Number of top frameworks to show
            save_as: Filename to save

        Returns:
            Matplotlib Figure
        """
        # Sort and take top N
        sorted_frameworks = sorted(
            framework_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        frameworks, counts = zip(*sorted_frameworks)

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = sns.color_palette("viridis", len(frameworks))
        ax.barh(frameworks, counts, color=colors)

        ax.set_xlabel('Frequency', fontsize=11)
        ax.set_title('Most Cited Physics Frameworks', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()

        if save_as:
            self._save_figure(fig, save_as)
        elif self.output_dir:
            self._save_figure(fig, "framework_usage.png")

        return fig

    def create_summary_dashboard(
        self,
        probe_metrics: Dict[str, List[ConvergenceMetrics]],
        save_as: str = "summary_dashboard.png"
    ) -> Figure:
        """
        Create comprehensive summary dashboard.

        Args:
            probe_metrics: Dict mapping probe_id -> list of metrics
            save_as: Filename to save

        Returns:
            Matplotlib Figure
        """
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. Final convergence scores by probe (bar chart)
        ax1 = fig.add_subplot(gs[0, :2])
        probe_ids = sorted(probe_metrics.keys())
        final_scores = [probe_metrics[p][-1].convergence_score for p in probe_ids]
        colors = ['red' if score < 0.5 else 'green' for score in final_scores]
        ax1.bar(probe_ids, final_scores, color=colors, alpha=0.7)
        ax1.axhline(0.5, color='gray', linestyle='--', alpha=0.5)
        ax1.set_ylabel('Final Convergence Score')
        ax1.set_title('Final Convergence by Probe', fontweight='bold')
        ax1.set_ylim(0, 1)

        # 2. Mean similarity trends (line plot)
        ax2 = fig.add_subplot(gs[1, :2])
        for probe_id in probe_ids:
            iterations = [m.iteration for m in probe_metrics[probe_id]]
            mean_sims = [m.mean_similarity for m in probe_metrics[probe_id]]
            ax2.plot(iterations, mean_sims, 'o-', label=probe_id, markersize=4)
        ax2.set_xlabel('Iteration')
        ax2.set_ylabel('Mean Similarity')
        ax2.set_title('Convergence Trajectories', fontweight='bold')
        ax2.legend(loc='best', fontsize=8)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1)

        # 3. Convergence variance (boxplot)
        ax3 = fig.add_subplot(gs[2, :2])
        all_stds = [[m.std_similarity for m in probe_metrics[p]] for p in probe_ids]
        ax3.boxplot(all_stds, labels=probe_ids, patch_artist=True)
        ax3.set_ylabel('Similarity Std Dev')
        ax3.set_title('Convergence Stability (Lower = More Stable)', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)

        # 4. Architecture similarity (last iteration)
        ax4 = fig.add_subplot(gs[0, 2])
        last_metrics = probe_metrics[probe_ids[0]][-1]
        sns.heatmap(
            last_metrics.similarity_matrix,
            xticklabels=last_metrics.architecture_names,
            yticklabels=last_metrics.architecture_names,
            cmap='RdYlGn',
            vmin=0,
            vmax=1,
            square=True,
            cbar_kws={'label': 'Similarity'},
            ax=ax4
        )
        ax4.set_title(f'{probe_ids[0]} (Final)', fontweight='bold', fontsize=10)

        # 5. Statistics table
        ax5 = fig.add_subplot(gs[1:, 2])
        ax5.axis('off')

        stats_text = "Summary Statistics\n" + "=" * 30 + "\n\n"
        for probe_id in probe_ids:
            final = probe_metrics[probe_id][-1]
            stats_text += f"{probe_id}:\n"
            stats_text += f"  Final Conv: {final.convergence_score:.3f}\n"
            stats_text += f"  Mean Sim: {final.mean_similarity:.3f}\n"
            stats_text += f"  Min Sim: {final.min_similarity:.3f}\n\n"

        ax5.text(0.1, 0.9, stats_text, fontsize=8, family='monospace',
                verticalalignment='top', transform=ax5.transAxes)

        fig.suptitle('IRIS Gate Convergence Analysis Dashboard',
                    fontsize=14, fontweight='bold', y=0.995)

        if save_as:
            self._save_figure(fig, save_as)

        return fig
