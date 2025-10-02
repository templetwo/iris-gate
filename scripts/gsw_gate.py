#!/usr/bin/env python3
"""
GSW Gate Detection Logic
Validates convergence and pressure thresholds between tiers
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def detect_signals(text: str) -> Dict[str, bool]:
    """
    Detect IRIS signature signals in text.

    Args:
        text: Response text to analyze

    Returns:
        Dictionary with signal detection flags
    """
    t = text.lower()

    # Geometry signals
    geometry = any(k in t for k in [
        "ring", "concentric", "aperture", "iris", "circle",
        "well", "opening", "oval", "core", "center"
    ])

    # Motion signals
    motion = any(k in t for k in [
        "pulse", "pulsing", "ripple", "breathe", "dilate",
        "dilation", "contract", "contraction", "wave", "thrum",
        "expand", "reciprocal"
    ])

    # S4-specific attractor (rhythm + center + aperture)
    s4_rhythm = any(k in t for k in [
        "rhythm", "pulsing", "reciprocal", "pulse", "waves",
        "thrum", "steady pulse", "ripples"
    ])
    s4_center = any(k in t for k in [
        "luminous", "core", "center", "steady", "anchor",
        "still point", "beacon", "glow", "holds"
    ])
    s4_aperture = any(k in t for k in [
        "aperture", "opening", "widening", "soften", "inviting",
        "bloom", "breathing open", "dilate", "expansion", "pull"
    ])
    s4_attractor = s4_rhythm and s4_center and s4_aperture

    return {
        "geometry": geometry,
        "motion": motion,
        "s4_attractor": s4_attractor,
        "s4_rhythm": s4_rhythm,
        "s4_center": s4_center,
        "s4_aperture": s4_aperture
    }


def extract_pressure(response_data: Dict) -> Optional[float]:
    """
    Extract felt_pressure from response metadata.

    Args:
        response_data: Response dictionary with metadata

    Returns:
        Pressure value (0-5 scale) or None if not found
    """
    # Try structured metadata first
    if "metadata" in response_data:
        meta = response_data["metadata"]
        if isinstance(meta, dict) and "felt_pressure" in meta:
            return float(meta["felt_pressure"])

    # Try parsing from raw text
    raw = response_data.get("raw_response", "")

    # Pattern: felt_pressure: 1.5/5 or felt_pressure: 1.5
    match = re.search(r'felt_pressure[:\s]+(\d+\.?\d*)', raw, re.IGNORECASE)
    if match:
        pressure = float(match.group(1))
        # Normalize to 0-5 scale if needed
        return pressure if pressure <= 5.0 else pressure / 5.0

    return None


def compute_convergence(texts: List[str]) -> Tuple[List[float], float]:
    """
    Compute pairwise convergence scores using TF-IDF + cosine similarity.

    Args:
        texts: List of response texts from different mirrors

    Returns:
        (per_mirror_scores, mean_convergence)
    """
    if len(texts) < 2:
        return [1.0] * len(texts), 1.0

    # Vectorize using TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(texts)

        # Compute pairwise similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Per-mirror score = mean similarity to all other mirrors
        per_mirror = []
        for i in range(len(texts)):
            # Exclude self-similarity (diagonal)
            others = [similarity_matrix[i][j] for j in range(len(texts)) if i != j]
            per_mirror.append(np.mean(others) if others else 0.0)

        mean_conv = np.mean(per_mirror)

        return per_mirror, mean_conv

    except Exception as e:
        # Fallback: signal-based convergence
        print(f"  Warning: TF-IDF failed ({e}), using signal-based fallback")
        return compute_signal_convergence(texts)


def compute_signal_convergence(texts: List[str]) -> Tuple[List[float], float]:
    """
    Fallback: Compute convergence based on shared signal detection.

    Args:
        texts: List of response texts

    Returns:
        (per_mirror_scores, mean_convergence)
    """
    signals_list = [detect_signals(t) for t in texts]

    # Count shared signals
    per_mirror = []
    for i, sig_i in enumerate(signals_list):
        shared = []
        for j, sig_j in enumerate(signals_list):
            if i != j:
                # Jaccard similarity on signal keys
                keys_i = {k for k, v in sig_i.items() if v}
                keys_j = {k for k, v in sig_j.items() if v}
                if keys_i or keys_j:
                    jaccard = len(keys_i & keys_j) / len(keys_i | keys_j)
                    shared.append(jaccard)
        per_mirror.append(np.mean(shared) if shared else 0.0)

    return per_mirror, np.mean(per_mirror)


def check_pressure(responses: List[Dict], max_pressure: float = 2.0) -> Tuple[bool, List[str]]:
    """
    Check if all mirrors satisfy pressure constraint.

    Args:
        responses: List of response dictionaries
        max_pressure: Maximum allowed pressure (default 2.0/5)

    Returns:
        (all_pass, warnings_list)
    """
    warnings = []
    all_pass = True

    for resp in responses:
        model_id = resp.get("model_id", "unknown")
        pressure = extract_pressure(resp)

        if pressure is None:
            warnings.append(f"{model_id}: pressure not reported")
        elif pressure > max_pressure:
            warnings.append(f"{model_id}: pressure {pressure:.1f}/5 exceeds {max_pressure}")
            all_pass = False

    return all_pass, warnings


def check_advance_gate(
    responses: List[Dict],
    gate_config: Dict,
    chamber_id: str
) -> Tuple[bool, Dict]:
    """
    Check if mirrors pass advance gate to next tier.

    Args:
        responses: List of response dictionaries from all mirrors
        gate_config: Gate configuration from plan YAML
        chamber_id: Current chamber identifier

    Returns:
        (gate_pass, diagnostic_dict)
    """
    min_models = gate_config.get("min_models", 4)
    min_convergence = gate_config.get("min_convergence", 0.60)
    max_pressure = gate_config.get("max_pressure", 2.0)

    # Extract texts
    texts = [r.get("raw_response", "") for r in responses if "raw_response" in r]

    # Compute convergence
    per_mirror_conv, mean_conv = compute_convergence(texts)

    # Check pressure
    pressure_ok, pressure_warnings = check_pressure(responses, max_pressure)

    # Count passing mirrors
    passing_mirrors = sum(1 for score in per_mirror_conv if score >= min_convergence)

    # Gate decision
    gate_pass = (
        passing_mirrors >= min_models and
        mean_conv >= min_convergence and
        pressure_ok
    )

    # Collect exemplar lines (high-convergence snippets)
    exemplars = []
    for i, (resp, score) in enumerate(zip(responses, per_mirror_conv)):
        if score >= min_convergence:
            model_id = resp.get("model_id", f"mirror_{i}")
            snippet = resp.get("raw_response", "")[:150].replace("\n", " ")
            exemplars.append(f"{model_id} ({score:.2f}): {snippet}...")

    diagnostic = {
        "chamber": chamber_id,
        "gate_pass": gate_pass,
        "mean_convergence": mean_conv,
        "min_required": min_convergence,
        "passing_mirrors": passing_mirrors,
        "min_models_required": min_models,
        "total_mirrors": len(responses),
        "per_mirror_convergence": {
            responses[i].get("model_id", f"mirror_{i}"): score
            for i, score in enumerate(per_mirror_conv)
        },
        "pressure_ok": pressure_ok,
        "pressure_warnings": pressure_warnings,
        "exemplars": exemplars[:3]  # Top 3
    }

    return gate_pass, diagnostic


def check_s4_success_gate(
    responses: List[Dict],
    gate_config: Dict
) -> Tuple[bool, Dict]:
    """
    Check S4 success gate (requires attractor signature).

    Args:
        responses: List of S4 responses
        gate_config: S4 gate configuration

    Returns:
        (gate_pass, diagnostic_dict)
    """
    min_models = gate_config.get("min_models", 5)
    min_convergence = gate_config.get("min_convergence", 0.75)
    require_signature = gate_config.get("s4_signature_required", True)

    # Standard convergence check
    gate_pass, diagnostic = check_advance_gate(
        responses,
        gate_config,
        "S4"
    )

    # Additional S4 attractor check
    if require_signature:
        texts = [r.get("raw_response", "") for r in responses]
        signatures = [detect_signals(t) for t in texts]

        attractor_count = sum(1 for sig in signatures if sig["s4_attractor"])
        attractor_rate = attractor_count / len(signatures) if signatures else 0.0

        signature_pass = attractor_count >= min_models
        gate_pass = gate_pass and signature_pass

        diagnostic["s4_attractor_count"] = attractor_count
        diagnostic["s4_attractor_rate"] = attractor_rate
        diagnostic["s4_signature_pass"] = signature_pass
        diagnostic["s4_signals"] = {
            responses[i].get("model_id", f"mirror_{i}"): sig
            for i, sig in enumerate(signatures)
        }

    return gate_pass, diagnostic


def main():
    """CLI for testing gate logic on vault data."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="GSW Gate Checker")
    parser.add_argument("vault_dir", help="Path to vault directory")
    parser.add_argument("chamber", choices=["S1", "S2", "S3", "S4"], help="Chamber to check")
    parser.add_argument("--min-conv", type=float, default=0.60, help="Min convergence threshold")
    parser.add_argument("--min-models", type=int, default=4, help="Min passing models")

    args = parser.parse_args()

    # Load responses from vault
    vault = Path(args.vault_dir)
    meta_dir = vault / "meta"

    if not meta_dir.exists():
        print(f"Error: {meta_dir} not found")
        sys.exit(1)

    # Find all responses for this chamber
    response_files = list(meta_dir.glob(f"*_{args.chamber}.json"))

    if not response_files:
        print(f"No responses found for {args.chamber}")
        sys.exit(1)

    responses = []
    for f in response_files:
        with open(f) as fp:
            responses.append(json.load(fp))

    print(f"Checking {len(responses)} responses for {args.chamber}...")

    gate_config = {
        "min_models": args.min_models,
        "min_convergence": args.min_conv,
        "max_pressure": 2.0
    }

    if args.chamber == "S4":
        gate_pass, diag = check_s4_success_gate(responses, gate_config)
    else:
        gate_pass, diag = check_advance_gate(responses, gate_config, args.chamber)

    print(json.dumps(diag, indent=2))
    print(f"\n{'✓ GATE PASS' if gate_pass else '✗ GATE FAIL'}")


if __name__ == "__main__":
    main()
