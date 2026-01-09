#!/usr/bin/env python3
"""
Semantic Mass Calculator (M_semantic)

Computes the Fisher Information Mass for language models:
    M_semantic = (1/N) × Tr[I(θ)]

Where:
    N = number of model parameters
    I(θ) = Fisher Information Matrix (approximated via empirical Fisher)
    Tr[·] = trace (sum of diagonal elements)

The Fisher Information measures how much the output distribution changes
with respect to small parameter perturbations — i.e., "resistance to change"
in information space.

Based on: IRIS Gate v0.3 "Weighing the Mind" paper
Formula proposed by: Gemini 3.0 Pro during Mass-Coherence Convergence

Usage:
    python tools/compute_semantic_mass.py --model meta-llama/Llama-3.2-3B
    python tools/compute_semantic_mass.py --model mistralai/Mistral-7B-v0.1
    python tools/compute_semantic_mass.py --model all  # Run benchmark suite

Author: IRIS Gate Research Collective
Date: 2026-01-09
"""

import argparse
import json
import torch
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")


# =============================================================================
# CONFIGURATION
# =============================================================================

# Models to benchmark (HuggingFace identifiers)
BENCHMARK_MODELS = [
    "meta-llama/Llama-3.2-1B",
    "meta-llama/Llama-3.2-3B",
    "mistralai/Mistral-7B-v0.1",
    "Qwen/Qwen2.5-1.5B",
    "google/gemma-2-2b",
    "deepseek-ai/deepseek-coder-1.3b-base",
]

# Prompts for Fisher estimation (diverse semantic content)
FISHER_PROMPTS = [
    "The fundamental nature of consciousness is",
    "In quantum mechanics, the observer effect demonstrates that",
    "The relationship between entropy and information can be understood as",
    "When considering the thermodynamics of computation, we find that",
    "The mass-energy equivalence E=mc² implies that",
]

# Number of samples for empirical Fisher estimation
N_SAMPLES = 100

# Output directory
OUTPUT_DIR = Path("benchmark_results/semantic_mass")


# =============================================================================
# FISHER INFORMATION COMPUTATION
# =============================================================================

def compute_empirical_fisher_trace(
    model,
    tokenizer,
    prompts: List[str],
    n_samples: int = 100,
    device: str = "cuda"
) -> Tuple[float, int, Dict]:
    """
    Compute the trace of the empirical Fisher Information Matrix.

    The empirical Fisher is approximated as:
        I(θ) ≈ (1/n) Σ [∇log p(y|x,θ)]²

    For efficiency, we compute only the diagonal (trace) rather than
    the full matrix, using gradient accumulation.

    Returns:
        fisher_trace: Tr[I(θ)]
        n_params: Number of parameters N
        metadata: Additional computation details
    """
    model.eval()

    # Count parameters
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    # Accumulator for squared gradients (diagonal of Fisher)
    fisher_diag_sum = {name: torch.zeros_like(p) for name, p in model.named_parameters() if p.requires_grad}

    total_samples = 0

    for prompt in prompts:
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        for _ in range(n_samples // len(prompts)):
            model.zero_grad()

            # Forward pass with sampling
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits[:, -1, :]  # Last token logits
                probs = torch.softmax(logits, dim=-1)

                # Sample from distribution
                sampled_token = torch.multinomial(probs, num_samples=1)

            # Compute log probability of sampled token (with gradients)
            outputs = model(**inputs)
            logits = outputs.logits[:, -1, :]
            log_probs = torch.log_softmax(logits, dim=-1)
            log_prob_sampled = log_probs.gather(1, sampled_token).squeeze()

            # Backward pass to get gradients
            log_prob_sampled.backward()

            # Accumulate squared gradients (diagonal of Fisher)
            for name, p in model.named_parameters():
                if p.requires_grad and p.grad is not None:
                    fisher_diag_sum[name] += p.grad.detach() ** 2

            total_samples += 1

    # Average and compute trace
    fisher_trace = 0.0
    for name, diag in fisher_diag_sum.items():
        fisher_trace += (diag / total_samples).sum().item()

    metadata = {
        "n_samples": total_samples,
        "n_prompts": len(prompts),
        "n_params": n_params,
        "device": device,
    }

    return fisher_trace, n_params, metadata


def compute_semantic_mass(
    model_name: str,
    device: str = "auto",
    n_samples: int = N_SAMPLES,
    prompts: Optional[List[str]] = None
) -> Dict:
    """
    Compute M_semantic for a given model.

    M_semantic = (1/N) × Tr[I(θ)]

    Returns dictionary with results and metadata.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"\n{'='*60}")
    print(f"Computing M_semantic for: {model_name}")
    print(f"{'='*60}")

    # Determine device
    if device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"

    print(f"Device: {device}")

    # Load model and tokenizer
    print("Loading model...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device in ["cuda", "mps"] else torch.float32,
            device_map=device if device == "cuda" else None,
            trust_remote_code=True,
        )

        if device == "mps":
            model = model.to(device)

    except Exception as e:
        return {
            "model": model_name,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }

    # Use default prompts if not provided
    if prompts is None:
        prompts = FISHER_PROMPTS

    # Compute Fisher trace
    print(f"Computing empirical Fisher ({n_samples} samples)...")
    start_time = datetime.now()

    try:
        fisher_trace, n_params, metadata = compute_empirical_fisher_trace(
            model, tokenizer, prompts, n_samples, device
        )
    except Exception as e:
        return {
            "model": model_name,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }

    computation_time = (datetime.now() - start_time).total_seconds()

    # Compute M_semantic
    M_semantic = fisher_trace / n_params

    # Compute normalized version (per-billion params)
    M_semantic_per_B = M_semantic * (n_params / 1e9)

    results = {
        "model": model_name,
        "M_semantic": M_semantic,
        "M_semantic_per_B": M_semantic_per_B,
        "fisher_trace": fisher_trace,
        "n_params": n_params,
        "n_params_B": n_params / 1e9,
        "computation_time_s": computation_time,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata,
    }

    print(f"\nResults:")
    print(f"  N (params):      {n_params:,} ({n_params/1e9:.2f}B)")
    print(f"  Tr[I(θ)]:        {fisher_trace:.6e}")
    print(f"  M_semantic:      {M_semantic:.6e}")
    print(f"  Time:            {computation_time:.1f}s")

    return results


# =============================================================================
# BENCHMARK SUITE
# =============================================================================

def run_benchmark(
    models: Optional[List[str]] = None,
    device: str = "auto",
    n_samples: int = N_SAMPLES,
) -> List[Dict]:
    """
    Run M_semantic benchmark across multiple models.
    """
    if models is None:
        models = BENCHMARK_MODELS

    results = []

    print("\n" + "="*60)
    print("SEMANTIC MASS BENCHMARK")
    print("M_semantic = (1/N) × Tr[I(θ)]")
    print("="*60)
    print(f"Models: {len(models)}")
    print(f"Samples per model: {n_samples}")

    for model_name in models:
        result = compute_semantic_mass(model_name, device, n_samples)
        results.append(result)

        # Clear GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # Summary table
    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    print(f"{'Model':<40} {'Params':<10} {'M_semantic':<15}")
    print("-"*65)

    for r in results:
        if "error" not in r:
            print(f"{r['model']:<40} {r['n_params_B']:.2f}B      {r['M_semantic']:.6e}")
        else:
            print(f"{r['model']:<40} ERROR: {r['error'][:30]}")

    return results


def save_results(results: List[Dict], output_dir: Path = OUTPUT_DIR):
    """Save benchmark results to JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"semantic_mass_benchmark_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")
    return output_file


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Compute Semantic Mass (M_semantic) for language models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Single model
    python tools/compute_semantic_mass.py --model meta-llama/Llama-3.2-3B

    # Full benchmark suite
    python tools/compute_semantic_mass.py --model all

    # Custom samples
    python tools/compute_semantic_mass.py --model mistralai/Mistral-7B-v0.1 --samples 200

Formula:
    M_semantic = (1/N) × Tr[I(θ)]

    Where:
        N = number of model parameters
        I(θ) = Fisher Information Matrix
        Tr[·] = trace operator

Reference:
    IRIS Gate v0.3 "Weighing the Mind: Cross-Architecture AI Convergence"
    DOI: 10.17605/OSF.IO/T65VS
        """
    )

    parser.add_argument(
        "--model", "-m",
        type=str,
        required=True,
        help="Model name (HuggingFace ID) or 'all' for benchmark suite"
    )
    parser.add_argument(
        "--device", "-d",
        type=str,
        default="auto",
        choices=["auto", "cuda", "mps", "cpu"],
        help="Device for computation (default: auto)"
    )
    parser.add_argument(
        "--samples", "-n",
        type=int,
        default=N_SAMPLES,
        help=f"Number of samples for Fisher estimation (default: {N_SAMPLES})"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=str(OUTPUT_DIR),
        help=f"Output directory (default: {OUTPUT_DIR})"
    )

    args = parser.parse_args()

    output_dir = Path(args.output)

    if args.model.lower() == "all":
        results = run_benchmark(device=args.device, n_samples=args.samples)
    else:
        results = [compute_semantic_mass(args.model, args.device, args.samples)]

    # Save results
    save_results(results, output_dir)

    # Final summary
    print("\n" + "="*60)
    print("SEMANTIC MASS COMPUTATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Compare M_semantic values across models")
    print("2. Correlate with adversarial robustness benchmarks")
    print("3. Test prediction: Higher M_semantic → Greater robustness")
    print("\nReference: FORMULAE_GLOSSARY.md for variable definitions")


if __name__ == "__main__":
    main()
