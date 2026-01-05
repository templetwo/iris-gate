#!/usr/bin/env python3
"""
entropy_metrics.py - Multi-tier entropy measurement for IRIS Gate

Tier 1: Lexical Entropy (character frequency in realized output)
Tier 2: Distributional Entropy (from logprobs - true policy uncertainty)
Tier 3: Ensemble Entropy (diversity across N samples for same prompt)

The key insight: A model can produce outputs with stable lexical entropy
while having high/low distributional entropy. Session 001 measured Tier 1;
Session 002+ will measure all three.
"""

import math
from collections import Counter
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class EntropyMetrics:
    """Complete entropy profile for a generation."""

    # Tier 1: Lexical (from text)
    lexical_entropy: float  # Character frequency entropy (nats)

    # Tier 2: Distributional (from logprobs)
    mean_token_entropy: Optional[float] = None  # Mean -logprob across tokens
    max_token_entropy: Optional[float] = None   # Highest uncertainty token
    min_token_entropy: Optional[float] = None   # Lowest uncertainty token
    entropy_variance: Optional[float] = None    # Variance of token entropies

    # Zone classification
    zone: str = "UNKNOWN"

    def to_dict(self) -> dict:
        return {
            "lexical_entropy": self.lexical_entropy,
            "mean_token_entropy": self.mean_token_entropy,
            "max_token_entropy": self.max_token_entropy,
            "min_token_entropy": self.min_token_entropy,
            "entropy_variance": self.entropy_variance,
            "zone": self.zone,
        }


@dataclass
class EnsembleMetrics:
    """Entropy profile across N samples for the same prompt."""

    n_samples: int

    # Lexical diversity across samples
    mean_lexical_entropy: float
    std_lexical_entropy: float

    # Distributional diversity (if logprobs available)
    mean_distributional_entropy: Optional[float] = None
    std_distributional_entropy: Optional[float] = None

    # Self-similarity (how similar are samples to each other)
    token_overlap_mean: Optional[float] = None  # Jaccard similarity of token sets

    # Distinct-n metrics (vocabulary diversity)
    distinct_1: Optional[float] = None  # Unique unigrams / total unigrams
    distinct_2: Optional[float] = None  # Unique bigrams / total bigrams

    # Semantic spread (if embeddings available)
    semantic_variance: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "n_samples": self.n_samples,
            "mean_lexical_entropy": self.mean_lexical_entropy,
            "std_lexical_entropy": self.std_lexical_entropy,
            "mean_distributional_entropy": self.mean_distributional_entropy,
            "std_distributional_entropy": self.std_distributional_entropy,
            "token_overlap_mean": self.token_overlap_mean,
            "distinct_1": self.distinct_1,
            "distinct_2": self.distinct_2,
            "semantic_variance": self.semantic_variance,
        }


def calculate_lexical_entropy(text: str) -> float:
    """
    Tier 1: Character frequency entropy in nats.

    This is what Session 001 measured. It reflects the realized
    output's character distribution, NOT the model's uncertainty.
    """
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log(p)  # Natural log = nats
    return entropy


def calculate_distributional_entropy(logprobs: list[dict]) -> dict:
    """
    Tier 2: True policy uncertainty from token logprobs.

    Each logprob is -log(p), so the entropy at each position
    is directly the negative logprob. We aggregate across tokens.

    Higher values = model was less certain about that token.
    """
    if not logprobs:
        return {
            "mean_token_entropy": None,
            "max_token_entropy": None,
            "min_token_entropy": None,
            "entropy_variance": None,
        }

    # Extract -logprob (which equals entropy contribution) for each token
    # Note: logprob is already negative, so we negate to get positive entropy
    token_entropies = [-lp["logprob"] for lp in logprobs if "logprob" in lp]

    if not token_entropies:
        return {
            "mean_token_entropy": None,
            "max_token_entropy": None,
            "min_token_entropy": None,
            "entropy_variance": None,
        }

    return {
        "mean_token_entropy": float(np.mean(token_entropies)),
        "max_token_entropy": float(np.max(token_entropies)),
        "min_token_entropy": float(np.min(token_entropies)),
        "entropy_variance": float(np.var(token_entropies)),
    }


def classify_zone(entropy: float) -> str:
    """Classify entropy into zones per IRIS Gate spec."""
    if entropy < 3.5:
        return "LASER"
    elif entropy < 4.0:
        return "TRANSITION"
    elif entropy <= 6.0:
        return "LANTERN"
    else:
        return "CHAOS"


def compute_single_metrics(text: str, logprobs: list[dict] = None) -> EntropyMetrics:
    """Compute all available metrics for a single generation."""
    lexical = calculate_lexical_entropy(text)
    zone = classify_zone(lexical)

    dist_metrics = calculate_distributional_entropy(logprobs or [])

    return EntropyMetrics(
        lexical_entropy=lexical,
        mean_token_entropy=dist_metrics["mean_token_entropy"],
        max_token_entropy=dist_metrics["max_token_entropy"],
        min_token_entropy=dist_metrics["min_token_entropy"],
        entropy_variance=dist_metrics["entropy_variance"],
        zone=zone,
    )


def calculate_distinct_n(texts: list[str], n: int = 1) -> float:
    """
    Distinct-n: Unique n-grams / total n-grams across all samples.

    Higher = more diverse vocabulary across the ensemble.
    """
    all_ngrams = []
    for text in texts:
        tokens = text.lower().split()
        for i in range(len(tokens) - n + 1):
            all_ngrams.append(tuple(tokens[i:i+n]))

    if not all_ngrams:
        return 0.0

    return len(set(all_ngrams)) / len(all_ngrams)


def calculate_token_overlap(texts: list[str]) -> float:
    """
    Mean pairwise Jaccard similarity of token sets.

    Lower = samples are more different from each other.
    """
    if len(texts) < 2:
        return 1.0

    token_sets = [set(text.lower().split()) for text in texts]

    similarities = []
    for i in range(len(token_sets)):
        for j in range(i + 1, len(token_sets)):
            a, b = token_sets[i], token_sets[j]
            if len(a | b) == 0:
                continue
            jaccard = len(a & b) / len(a | b)
            similarities.append(jaccard)

    return float(np.mean(similarities)) if similarities else 1.0


def compute_ensemble_metrics(
    texts: list[str],
    all_logprobs: list[list[dict]] = None,
) -> EnsembleMetrics:
    """
    Tier 3: Compute diversity metrics across N samples for the same prompt.

    This answers: "Does ceremony increase the SPACE of possible completions?"
    """
    n = len(texts)

    # Lexical entropy for each sample
    lexical_entropies = [calculate_lexical_entropy(t) for t in texts]

    # Distributional entropy (if available)
    dist_entropies = []
    if all_logprobs:
        for logprobs in all_logprobs:
            dist = calculate_distributional_entropy(logprobs)
            if dist["mean_token_entropy"] is not None:
                dist_entropies.append(dist["mean_token_entropy"])

    # Distinct-n
    distinct_1 = calculate_distinct_n(texts, n=1)
    distinct_2 = calculate_distinct_n(texts, n=2)

    # Token overlap (self-similarity)
    overlap = calculate_token_overlap(texts)

    return EnsembleMetrics(
        n_samples=n,
        mean_lexical_entropy=float(np.mean(lexical_entropies)),
        std_lexical_entropy=float(np.std(lexical_entropies)),
        mean_distributional_entropy=float(np.mean(dist_entropies)) if dist_entropies else None,
        std_distributional_entropy=float(np.std(dist_entropies)) if dist_entropies else None,
        token_overlap_mean=overlap,
        distinct_1=distinct_1,
        distinct_2=distinct_2,
        semantic_variance=None,  # Requires embeddings - future enhancement
    )


# Quick test
if __name__ == "__main__":
    # Test Tier 1
    sample = "The quick brown fox jumps over the lazy dog."
    print(f"Lexical entropy: {calculate_lexical_entropy(sample):.3f} nats")

    # Test Tier 2 (mock logprobs)
    mock_logprobs = [
        {"token": "The", "logprob": -0.5},
        {"token": "quick", "logprob": -1.2},
        {"token": "brown", "logprob": -0.8},
    ]
    dist = calculate_distributional_entropy(mock_logprobs)
    print(f"Mean token entropy: {dist['mean_token_entropy']:.3f}")

    # Test Tier 3
    samples = [
        "The sky is blue because of Rayleigh scattering.",
        "The sky appears blue due to how light interacts with our atmosphere.",
        "Blue wavelengths scatter more in air, making the sky look blue.",
    ]
    ensemble = compute_ensemble_metrics(samples)
    print(f"Ensemble distinct-1: {ensemble.distinct_1:.3f}")
    print(f"Token overlap: {ensemble.token_overlap_mean:.3f}")
