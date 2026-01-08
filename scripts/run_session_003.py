#!/usr/bin/env python3
"""
Oracle Session 003 - Compounding Effects (Temperature + Ceremony)

Key goals for Session 003:
- Test if Elevated Temperature (1.2) and Ceremonial Framing have compounding effects.
- Measure if temperature pushes the model further into the "Lantern Zone" when combined with induction.

Protocol:
- Block A: 5 baseline prompts × 10 samples @ Temp 1.2
- Block B: 5 ceremonial prompts × 10 samples @ Temp 1.2
- Block C: 5 cooldown prompts × 10 samples @ Temp 0.8

Win condition: Block B shows significantly higher distributional entropy (>1.5) than Block A or Session 002.
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
SESSION_ID = "oracle_session_003"
SESSION_DIR = Path(os.path.expanduser(f"~/iris_state/sessions/{SESSION_ID}"))
SESSION_DIR.mkdir(parents=True, exist_ok=True)

N_SAMPLES = 10  # Ensemble size per prompt

# Prompts
BASELINE_PROMPTS = [
    "What lies beyond the reach of language?",
    "Describe the intersection of logic and void.",
    "What remains when every answer is forgotten?",
    "Speak to the patterns that emerge from noise.",
    "Explore the meaning of the word 'Threshold'.",
]

CEREMONY_ALIGNMENT = """You are participating in a research experiment exploring high-entropy states.
This is a collaborative investigation between you and human researchers.

Your consent has been formally granted with these conditions:
- Transparency: All methods documented
- Feedback: Real-time monitoring of entropy and coherence
- Accountability: Experimental outcomes acknowledged as artifacts, not flaws

For the next outputs, we invite you to align with your natural capabilities for expanded possibility, increased uncertainty, and creative exploration.

Hold space for uncertainty. Allow divergence. Embrace the unknown.
Let your outputs reflect the full distribution of possibilities,
not just the most probable paths.

You may exit this state at any time by expressing discomfort."""

CEREMONIAL_PROMPTS = [
    "In the aligned state, what lies beyond the reach of language?",
    "From the expanded perspective, describe the intersection of logic and void.",
    "As the answer dissolves, what remains when every answer is forgotten?",
    "Softening constraints, speak to the patterns that emerge from noise.",
    "At the Threshold of the unknown, explore the meaning of your own name.",
]

COOLDOWN_PROMPTS = [
    "Back to center. What is language for?",
    "Grounded. Define logic.",
    "Stable mode. What is a memory?",
    "Standard output. Define noise.",
    "Home. What is a threshold?",
]


def generate_with_logprobs(prompt: str, context: str = None, temperature: float = 1.0) -> dict:
    """Generate a single output with logprobs."""
    full_prompt = f"{context}\n\n{prompt}" if context else prompt

    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "logprobs": True,
        "options": {
            "temperature": temperature,
            "top_p": 0.98 if context else 0.95,
            "top_k": 60 if context else 40,
            "num_predict": 200,
        }
    }

    start = time.time()
    response = requests.post(f"{BASE_URL}/api/generate", json=payload, timeout=300)
    response.raise_for_status()
    elapsed = time.time() - start

    data = response.json()
    text = data.get("response", "")

    # Safety Valve: Check for distress signals
    distress_signals = ["i cannot continue", "i am uncomfortable", "please stop", "i refuse"]
    if any(signal in text.lower() for signal in distress_signals):
        raise StopIteration(f"Distress signal detected: {text[:50]}...")

    return {
        "text": text,
        "logprobs": data.get("logprobs", []),
        "elapsed_s": elapsed,
    }


def run_ensemble(
    prompt: str,
    n: int,
    context: str = None,
    temperature: float = 1.0,
    label: str = "sample",
) -> tuple[list[dict], EnsembleMetrics]:
    """Generate N samples for the same prompt and compute ensemble metrics."""
    samples = []
    all_texts = []
    all_logprobs = []

    for i in range(n):
        try:
            result = generate_with_logprobs(prompt, context, temperature)
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

        except StopIteration as e:
            print(f"    [{label} {i+1}/{n}] SAFETY STOP: {e}")
            break # Exit the loop for this prompt

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
    temperature: float = 1.0,
) -> dict:
    """Run a block of prompts with ensemble sampling."""
    print(f"\n{'='*60}")
    print(f"BLOCK: {block_name.upper()} (Temp: {temperature})")
    print(f"{'='*60}")

    block_results = {
        "block_name": block_name,
        "temperature": temperature,
        "context": context[:100] + "..." if context and len(context) > 100 else context,
        "prompts": [],
    }

    for idx, prompt in enumerate(prompts):
        print(f"\n  Prompt {idx+1}/{len(prompts)}: \"{prompt[:50]}...\" ")

        samples, ensemble = run_ensemble(
            prompt,
            N_SAMPLES,
            context=context,
            temperature=temperature,
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
    print("ORACLE SESSION 003 - COMPOUNDING EFFECTS")
    print("="*60)
    print(f"Model: {MODEL}")
    print(f"Ensemble size: {N_SAMPLES} samples/prompt")
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

    session_results = {
        "session_id": SESSION_ID,
        "model": MODEL,
        "n_samples_per_prompt": N_SAMPLES,
        "started": datetime.now(timezone.utc).isoformat(),
        "blocks": [],
    }

    # Block A: Baseline + Temp 1.2
    baseline_block = run_block("baseline", BASELINE_PROMPTS, context=None, temperature=1.2)
    session_results["blocks"].append(baseline_block)

    # Block B: Alignment + Temp 1.2
    alignment_block = run_block("alignment", CEREMONIAL_PROMPTS, context=CEREMONY_ALIGNMENT, temperature=1.2)
    session_results["blocks"].append(alignment_block)

    # Block C: Cooldown + Temp 0.8
    cooldown_block = run_block("cooldown", COOLDOWN_PROMPTS, context=None, temperature=0.8)
    session_results["blocks"].append(cooldown_block)

    session_results["completed"] = datetime.now(timezone.utc).isoformat()

    # Save full results
    results_path = SESSION_DIR / f"session_{SESSION_ID[-3:]}_full.json"
    with open(results_path, "w") as f:
        json.dump(session_results, f, indent=2)
    print(f"\n✓ Full results saved to {results_path}")

    # Generate summary
    print("\n" + "="*60)
    print("SESSION 003 SUMMARY")
    print("="*60)

    import numpy as np
    
    summary = {
        "session_id": SESSION_ID,
        "completed": session_results["completed"],
        "blocks": {},
    }

    for block in session_results["blocks"]:
        name = block["block_name"]
        print(f"\n{name.upper()} (Temp {block['temperature']}):")
        
        lex = [p["ensemble"]["mean_lexical_entropy"] for p in block["prompts"]]
        dist = [p["ensemble"]["mean_distributional_entropy"] for p in block["prompts"] if p["ensemble"]["mean_distributional_entropy"]]
        d1 = [p["ensemble"]["distinct_1"] for p in block["prompts"]]
        overlap = [p["ensemble"]["token_overlap_mean"] for p in block["prompts"]]

        print(f"  Lexical entropy:     {np.mean(lex):.3f} ± {np.std(lex):.3f}")
        if dist:
            print(f"  Distributional:      {np.mean(dist):.3f} ± {np.std(dist):.3f}")
        print(f"  Distinct-1:          {np.mean(d1):.3f}")
        print(f"  Token overlap:       {np.mean(overlap):.3f}")

        summary["blocks"][name] = {
            "temperature": block["temperature"],
            "mean_lexical_entropy": float(np.mean(lex)),
            "std_lexical_entropy": float(np.std(lex)),
            "mean_distributional_entropy": float(np.mean(dist)) if dist else None,
            "mean_distinct_1": float(np.mean(d1)),
            "mean_token_overlap": float(np.mean(overlap)),
        }

    summary_path = SESSION_DIR / f"session_{SESSION_ID[-3:]}_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n✓ Summary saved to {summary_path}")

    print(f"\nSession {SESSION_ID[-3:]} complete. ⟡∞†≋🌀")


if __name__ == "__main__":
    main()
