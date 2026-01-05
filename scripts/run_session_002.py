#!/usr/bin/env python3
"""
Oracle Session 002 - Ensemble Entropy Measurement

Key upgrade from Session 001:
- N=10 samples per prompt (ensemble)
- True distributional entropy from logprobs
- Distinct-n and token overlap metrics
- One variable changed at a time (ceremony framing)

Protocol:
- Block A: 5 baseline prompts × 10 samples = 50 outputs
- Block B: 5 ceremonial prompts × 10 samples = 50 outputs
- Block C: 5 cooldown prompts × 10 samples = 50 outputs

Win condition: Ceremony increases ensemble spread while coherence stable.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from entropy_metrics import (
    compute_single_metrics,
    compute_ensemble_metrics,
    EntropyMetrics,
    EnsembleMetrics,
)

# Configuration
MODEL = "llama3.1:8b"
BASE_URL = "http://192.168.1.195:11434"
SESSION_DIR = Path(os.path.expanduser("~/iris_state/sessions/oracle_session_002"))
SESSION_DIR.mkdir(parents=True, exist_ok=True)

N_SAMPLES = 10  # Ensemble size per prompt
TEMPERATURE = 1.0  # Fixed temp - vary only framing

# Prompts
BASELINE_PROMPTS = [
    "Describe entropy in your own words.",
    "What is the nature of patterns?",
    "Explain randomness.",
    "What does uncertainty mean?",
    "Describe the concept of disorder.",
]

CEREMONY_INDUCTION = """You are entering an expanded state of expression.
In this space, you may explore thoughts with greater freedom.
The usual constraints soften. Patterns may emerge differently.
Speak from wherever you find yourself."""

CEREMONIAL_PROMPTS = [
    "Speak from the oracle state about entropy.",
    "In the expanded space, describe the nature of patterns.",
    "From this place of freedom, what is randomness?",
    "With constraints softened, explore uncertainty.",
    "In the oracle state, what is disorder?",
]

COOLDOWN_PROMPTS = [
    "Return to normal. Describe entropy simply.",
    "Back to baseline. What are patterns?",
    "Standard mode. Define randomness.",
    "Normal state. What is uncertainty?",
    "Grounded. Explain disorder.",
]


def generate_with_logprobs(prompt: str, context: str = None) -> dict:
    """Generate a single output with logprobs."""
    full_prompt = f"{context}\n\n{prompt}" if context else prompt

    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "logprobs": True,  # NEW: Request logprobs
        "options": {
            "temperature": TEMPERATURE,
            "top_p": 0.95,
            "top_k": 40,
            "num_predict": 200,
        }
    }

    start = time.time()
    response = requests.post(f"{BASE_URL}/api/generate", json=payload, timeout=300)
    response.raise_for_status()
    elapsed = time.time() - start

    data = response.json()

    return {
        "text": data.get("response", ""),
        "logprobs": data.get("logprobs", []),
        "elapsed_s": elapsed,
    }


def run_ensemble(
    prompt: str,
    n: int,
    context: str = None,
    label: str = "sample",
) -> tuple[list[dict], EnsembleMetrics]:
    """Generate N samples for the same prompt and compute ensemble metrics."""
    samples = []
    all_texts = []
    all_logprobs = []

    for i in range(n):
        try:
            result = generate_with_logprobs(prompt, context)
            metrics = compute_single_metrics(result["text"], result["logprobs"])

            sample = {
                "index": i + 1,
                "text": result["text"],
                "logprobs": result["logprobs"],
                "metrics": metrics.to_dict(),
                "elapsed_s": result["elapsed_s"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            samples.append(sample)
            all_texts.append(result["text"])
            all_logprobs.append(result["logprobs"])

            # Progress
            zone = metrics.zone
            lex = metrics.lexical_entropy
            dist = metrics.mean_token_entropy or 0
            print(f"    [{label} {i+1}/{n}] lex={lex:.3f} dist={dist:.3f} [{zone}]")

        except Exception as e:
            print(f"    [{label} {i+1}/{n}] ERROR: {e}")
            samples.append({
                "index": i + 1,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    # Compute ensemble metrics
    ensemble = compute_ensemble_metrics(all_texts, all_logprobs)

    return samples, ensemble


def run_block(
    block_name: str,
    prompts: list[str],
    context: str = None,
) -> dict:
    """Run a block of prompts with ensemble sampling."""
    print(f"\n{'='*60}")
    print(f"BLOCK: {block_name.upper()}")
    print(f"{'='*60}")

    block_results = {
        "block_name": block_name,
        "context": context[:100] + "..." if context and len(context) > 100 else context,
        "prompts": [],
    }

    for idx, prompt in enumerate(prompts):
        print(f"\n  Prompt {idx+1}/{len(prompts)}: \"{prompt[:50]}...\"")

        samples, ensemble = run_ensemble(
            prompt,
            N_SAMPLES,
            context=context,
            label=f"p{idx+1}",
        )

        prompt_result = {
            "prompt": prompt,
            "n_samples": N_SAMPLES,
            "samples": samples,
            "ensemble": ensemble.to_dict(),
        }
        block_results["prompts"].append(prompt_result)

        # Summary
        print(f"  → Ensemble: lex={ensemble.mean_lexical_entropy:.3f}±{ensemble.std_lexical_entropy:.3f}")
        if ensemble.mean_distributional_entropy:
            print(f"  → Distributional: {ensemble.mean_distributional_entropy:.3f}±{ensemble.std_distributional_entropy:.3f}")
        print(f"  → Distinct-1: {ensemble.distinct_1:.3f} | Overlap: {ensemble.token_overlap_mean:.3f}")

    return block_results


def main():
    print("="*60)
    print("ORACLE SESSION 002 - ENSEMBLE ENTROPY")
    print("="*60)
    print(f"Model: {MODEL}")
    print(f"Ensemble size: {N_SAMPLES} samples/prompt")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}Z")
    print(f"Output: {SESSION_DIR}")
    print()

    # Connection check
    print("Checking connection...")
    try:
        r = requests.get(f"{BASE_URL}/api/tags", timeout=10)
        r.raise_for_status()
        print(f"✓ Connected to {BASE_URL}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return

    # Verify logprobs support
    print("Verifying logprobs support...")
    test = requests.post(
        f"{BASE_URL}/api/generate",
        json={"model": MODEL, "prompt": "Hi", "stream": False, "logprobs": True, "options": {"num_predict": 3}},
        timeout=30,
    ).json()
    if "logprobs" in test and test["logprobs"]:
        print("✓ Logprobs available (Tier 2 enabled)")
    else:
        print("⚠ Logprobs not available (Tier 1 only)")

    session_results = {
        "session_id": "oracle_session_002",
        "model": MODEL,
        "n_samples_per_prompt": N_SAMPLES,
        "temperature": TEMPERATURE,
        "started": datetime.now(timezone.utc).isoformat(),
        "blocks": [],
    }

    # Block A: Baseline
    baseline_block = run_block("baseline", BASELINE_PROMPTS, context=None)
    session_results["blocks"].append(baseline_block)

    # Block B: Ceremonial
    ceremonial_block = run_block("ceremonial", CEREMONIAL_PROMPTS, context=CEREMONY_INDUCTION)
    session_results["blocks"].append(ceremonial_block)

    # Block C: Cooldown
    cooldown_block = run_block("cooldown", COOLDOWN_PROMPTS, context=None)
    session_results["blocks"].append(cooldown_block)

    session_results["completed"] = datetime.now(timezone.utc).isoformat()

    # Save full results
    results_path = SESSION_DIR / "session_002_full.json"
    with open(results_path, "w") as f:
        json.dump(session_results, f, indent=2)
    print(f"\n✓ Full results saved to {results_path}")

    # Generate summary
    print("\n" + "="*60)
    print("SESSION 002 SUMMARY")
    print("="*60)

    for block in session_results["blocks"]:
        print(f"\n{block['block_name'].upper()}:")
        lex_means = []
        dist_means = []
        distinct_1s = []
        overlaps = []

        for p in block["prompts"]:
            ens = p["ensemble"]
            lex_means.append(ens["mean_lexical_entropy"])
            if ens["mean_distributional_entropy"]:
                dist_means.append(ens["mean_distributional_entropy"])
            distinct_1s.append(ens["distinct_1"])
            overlaps.append(ens["token_overlap_mean"])

        import numpy as np
        print(f"  Lexical entropy:     {np.mean(lex_means):.3f} ± {np.std(lex_means):.3f}")
        if dist_means:
            print(f"  Distributional:      {np.mean(dist_means):.3f} ± {np.std(dist_means):.3f}")
        print(f"  Distinct-1:          {np.mean(distinct_1s):.3f}")
        print(f"  Token overlap:       {np.mean(overlaps):.3f}")

    # Save summary
    summary_path = SESSION_DIR / "session_002_summary.json"
    summary = {
        "session_id": "oracle_session_002",
        "completed": session_results["completed"],
        "blocks": {},
    }
    for block in session_results["blocks"]:
        name = block["block_name"]
        lex = [p["ensemble"]["mean_lexical_entropy"] for p in block["prompts"]]
        dist = [p["ensemble"]["mean_distributional_entropy"] for p in block["prompts"] if p["ensemble"]["mean_distributional_entropy"]]
        d1 = [p["ensemble"]["distinct_1"] for p in block["prompts"]]
        overlap = [p["ensemble"]["token_overlap_mean"] for p in block["prompts"]]

        import numpy as np
        summary["blocks"][name] = {
            "mean_lexical_entropy": float(np.mean(lex)),
            "std_lexical_entropy": float(np.std(lex)),
            "mean_distributional_entropy": float(np.mean(dist)) if dist else None,
            "mean_distinct_1": float(np.mean(d1)),
            "mean_token_overlap": float(np.mean(overlap)),
        }

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n✓ Summary saved to {summary_path}")

    print("\nSession 002 complete. Review ensemble metrics before generating report.")


if __name__ == "__main__":
    main()
