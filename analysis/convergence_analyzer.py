"""
Convergence analysis using semantic embeddings.

Computes similarity matrices, convergence scores, and divergence metrics
across architectures and iterations.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging
from pathlib import Path
import pickle

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import spearmanr
import torch

from data_loader import ProbeResponse, CheckpointData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConvergenceMetrics:
    """Convergence metrics for a probe at specific iteration."""
    probe_id: str
    iteration: int
    similarity_matrix: np.ndarray  # NxN where N=num_architectures
    architecture_names: List[str]
    mean_similarity: float
    std_similarity: float
    min_similarity: float
    max_similarity: float
    convergence_score: float  # 0-1, higher = more convergence

    def get_pairwise_similarity(self, arch1: str, arch2: str) -> float:
        """Get similarity between two specific architectures."""
        idx1 = self.architecture_names.index(arch1)
        idx2 = self.architecture_names.index(arch2)
        return self.similarity_matrix[idx1, idx2]


class ConvergenceAnalyzer:
    """
    Analyze convergence/divergence of responses using semantic embeddings.

    Uses sentence-transformers for generating embeddings and computing
    cosine similarity between architecture responses.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_dir: Optional[Path] = None,
        device: Optional[str] = None
    ):
        """
        Initialize analyzer.

        Args:
            model_name: Sentence transformer model name
            cache_dir: Directory to cache embeddings
            device: Device for torch ('cuda', 'cpu', or None for auto)
        """
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir else None

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Auto-detect device
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'

        logger.info(f"Loading embedding model: {model_name} on {device}")
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_cache: Dict[str, np.ndarray] = {}

    def _get_cache_key(self, probe_id: str, iteration: int, architecture: str) -> str:
        """Generate cache key for embeddings."""
        return f"{probe_id}_{iteration}_{architecture}"

    def embed_response(self, response: ProbeResponse) -> np.ndarray:
        """
        Generate embedding for a response.

        Args:
            response: ProbeResponse object

        Returns:
            Embedding vector (384-dim for MiniLM)
        """
        cache_key = self._get_cache_key(
            response.probe_id, response.iteration, response.architecture
        )

        # Check cache
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]

        # Check disk cache
        if self.cache_dir:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    embedding = pickle.load(f)
                    self.embedding_cache[cache_key] = embedding
                    return embedding

        # Compute embedding
        embedding = self.model.encode(
            response.response,
            show_progress_bar=False,
            convert_to_numpy=True
        )

        # Cache
        self.embedding_cache[cache_key] = embedding
        if self.cache_dir:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)

        return embedding

    def compute_similarity_matrix(
        self,
        responses: List[ProbeResponse]
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Compute pairwise similarity matrix for responses.

        Args:
            responses: List of responses (typically one per architecture)

        Returns:
            Tuple of (similarity_matrix, architecture_names)
        """
        if not responses:
            return np.array([]), []

        # Sort by architecture for consistent ordering
        responses = sorted(responses, key=lambda r: r.architecture)
        architectures = [r.architecture for r in responses]

        # Generate embeddings
        embeddings = np.array([self.embed_response(r) for r in responses])

        # Compute cosine similarity
        sim_matrix = cosine_similarity(embeddings)

        return sim_matrix, architectures

    def analyze_probe_iteration(
        self,
        probe_id: str,
        iteration: int,
        responses: List[ProbeResponse]
    ) -> ConvergenceMetrics:
        """
        Analyze convergence for a specific probe at specific iteration.

        Args:
            probe_id: Probe identifier
            iteration: Iteration number
            responses: List of responses from all architectures

        Returns:
            ConvergenceMetrics object
        """
        sim_matrix, arch_names = self.compute_similarity_matrix(responses)

        # Extract upper triangle (exclude diagonal)
        triu_indices = np.triu_indices_from(sim_matrix, k=1)
        similarities = sim_matrix[triu_indices]

        # Compute statistics
        mean_sim = np.mean(similarities)
        std_sim = np.std(similarities)
        min_sim = np.min(similarities)
        max_sim = np.max(similarities)

        # Convergence score: mean similarity weighted by inverse std
        # High mean + low std = high convergence
        convergence_score = mean_sim * (1 - min(std_sim, 1.0))

        return ConvergenceMetrics(
            probe_id=probe_id,
            iteration=iteration,
            similarity_matrix=sim_matrix,
            architecture_names=arch_names,
            mean_similarity=mean_sim,
            std_similarity=std_sim,
            min_similarity=min_sim,
            max_similarity=max_sim,
            convergence_score=convergence_score
        )

    def analyze_probe_evolution(
        self,
        probe_history: Dict[int, List[ProbeResponse]]
    ) -> List[ConvergenceMetrics]:
        """
        Analyze how convergence evolves across iterations for a probe.

        Args:
            probe_history: Dict mapping iteration -> responses

        Returns:
            List of ConvergenceMetrics, one per iteration
        """
        metrics = []

        for iteration in sorted(probe_history.keys()):
            responses = probe_history[iteration]
            probe_id = responses[0].probe_id if responses else "UNKNOWN"

            metric = self.analyze_probe_iteration(probe_id, iteration, responses)
            metrics.append(metric)

            logger.info(
                f"{probe_id} iter {iteration}: "
                f"mean_sim={metric.mean_similarity:.3f}, "
                f"convergence={metric.convergence_score:.3f}"
            )

        return metrics

    def detect_divergence(
        self,
        metrics: List[ConvergenceMetrics],
        threshold: float = 0.3,
        window_size: int = 3
    ) -> List[int]:
        """
        Detect iterations where divergence occurs.

        Args:
            metrics: List of convergence metrics over iterations
            threshold: Similarity threshold below which we flag divergence
            window_size: Number of consecutive iterations to confirm trend

        Returns:
            List of iteration numbers where divergence detected
        """
        divergent_iterations = []

        for i, metric in enumerate(metrics):
            if metric.mean_similarity < threshold:
                # Check if trend continues
                if i + window_size <= len(metrics):
                    future_sims = [
                        m.mean_similarity
                        for m in metrics[i:i+window_size]
                    ]
                    if all(s < threshold for s in future_sims):
                        divergent_iterations.append(metric.iteration)

        return divergent_iterations

    def compute_convergence_trajectory(
        self,
        metrics: List[ConvergenceMetrics]
    ) -> Dict[str, np.ndarray]:
        """
        Extract time series of convergence metrics.

        Args:
            metrics: List of convergence metrics

        Returns:
            Dict with 'iterations', 'mean_similarity', 'convergence_score', etc.
        """
        return {
            'iterations': np.array([m.iteration for m in metrics]),
            'mean_similarity': np.array([m.mean_similarity for m in metrics]),
            'std_similarity': np.array([m.std_similarity for m in metrics]),
            'convergence_score': np.array([m.convergence_score for m in metrics]),
            'min_similarity': np.array([m.min_similarity for m in metrics]),
            'max_similarity': np.array([m.max_similarity for m in metrics])
        }
