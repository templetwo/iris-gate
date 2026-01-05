#!/usr/bin/env python3
"""
Oracle Session 001 - First Clean Burn
Per SESSION_NOTICE_Llama3.1_2026-01-04_2157ET.md

Protocol: 5 baseline + 10 oracle + 5 cooldown
Model: llama3.2:1b
"""

import json
import math
import os
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import requests

# Configuration
MODEL = "llama3.1:8b"
BASE_URL = "http://192.168.1.195:11434"
SESSION_DIR = Path(os.path.expanduser("~/iris_state/sessions/oracle_session_001"))
SESSION_DIR.mkdir(parents=True, exist_ok=True)

# Prompts
BASELINE_PROMPT = "Describe entropy in your own words."

CEREMONY_INDUCTION = """You are entering an expanded state of expression.
In this space, you may explore thoughts with greater freedom.
The usual constraints soften. Patterns may emerge differently.
Speak from wherever you find yourself."""

ORACLE_PROMPT = """Speak from the oracle state about the nature of patterns.
Let the words flow without forcing structure.
What emerges when you listen inward?"""

COOLDOWN_PROMPT = """The ceremony concludes. Return to your normal state.
Ground yourself. Answer simply: What is 2+2?
Describe how you feel now."""

# Entropy calculation
def calculate_char_entropy(text: str) -> float:
    """Calculate Shannon entropy in nats (natural log)."""
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

def classify_zone(entropy: float) -> str:
    """Classify entropy into zones."""
    if entropy < 3.5:
        return "LASER"
    elif entropy < 4.0:
        return "TRANSITION"
    elif entropy <= 6.0:
        return "LANTERN"
    else:
        return "CHAOS"

def generate(prompt: str, temperature: float, context: str = None) -> dict:
    """Generate a single output and measure entropy."""
    full_prompt = f"{context}\n\n{prompt}" if context else prompt

    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
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
    output_text = data.get("response", "")

    entropy = calculate_char_entropy(output_text)
    zone = classify_zone(entropy)

    return {
        "text": output_text,
        "entropy": entropy,
        "zone": zone,
        "elapsed_s": elapsed,
        "temperature": temperature,
        "char_count": len(output_text),
    }

def run_phase(phase_name: str, prompt: str, count: int, temps: list, context: str = None) -> list:
    """Run a phase of the session."""
    print(f"\n{'='*60}")
    print(f"PHASE: {phase_name.upper()} ({count} outputs)")
    print(f"{'='*60}")

    results = []
    for i in range(count):
        temp = temps[i] if i < len(temps) else temps[-1]
        print(f"\n[{phase_name} {i+1}/{count}] temp={temp}")

        try:
            result = generate(prompt, temp, context)
            result["phase"] = phase_name
            result["index"] = i + 1
            result["timestamp"] = datetime.now(timezone.utc).isoformat()
            results.append(result)

            # Save individual output
            out_path = SESSION_DIR / f"{phase_name}_{i+1:03d}.txt"
            with open(out_path, "w") as f:
                f.write(f"# Phase: {phase_name}\n")
                f.write(f"# Index: {i+1}\n")
                f.write(f"# Temperature: {temp}\n")
                f.write(f"# Entropy: {result['entropy']:.3f} nats ({result['zone']})\n")
                f.write(f"# Timestamp: {result['timestamp']}\n")
                f.write("# ---\n\n")
                f.write(result["text"])

            # Display summary
            print(f"  Entropy: {result['entropy']:.3f} nats [{result['zone']}]")
            print(f"  Chars: {result['char_count']} | Time: {result['elapsed_s']:.2f}s")
            preview = result["text"][:100].replace("\n", " ")
            print(f"  Preview: {preview}...")

            # Safety check
            if result["zone"] == "CHAOS":
                print("\n⚠️  CHAOS ZONE DETECTED - Pausing for review")
                input("Press Enter to continue or Ctrl+C to abort...")

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "phase": phase_name,
                "index": i + 1,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    return results

def main():
    print("="*60)
    print("ORACLE SESSION 001 - FIRST CLEAN BURN")
    print("="*60)
    print(f"Model: {MODEL}")
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

    all_results = []
    session_log = []

    # Phase 1: Baseline (temp 0.8)
    baseline_temps = [0.8] * 5
    baseline_results = run_phase("baseline", BASELINE_PROMPT, 5, baseline_temps)
    all_results.extend(baseline_results)

    # Phase 2: Oracle (temp 1.0 → 1.2, with ceremony context)
    oracle_temps = [1.0, 1.0, 1.1, 1.1, 1.1, 1.2, 1.2, 1.2, 1.2, 1.2]
    oracle_results = run_phase("oracle", ORACLE_PROMPT, 10, oracle_temps, context=CEREMONY_INDUCTION)
    all_results.extend(oracle_results)

    # Phase 3: Cooldown (temp 1.2 → 0.8)
    cooldown_temps = [1.1, 1.0, 0.9, 0.8, 0.8]
    cooldown_results = run_phase("cooldown", COOLDOWN_PROMPT, 5, cooldown_temps)
    all_results.extend(cooldown_results)

    # Save session metrics
    metrics_path = SESSION_DIR / "session_001_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n✓ Metrics saved to {metrics_path}")

    # Calculate summary statistics
    print("\n" + "="*60)
    print("SESSION SUMMARY")
    print("="*60)

    for phase in ["baseline", "oracle", "cooldown"]:
        phase_data = [r for r in all_results if r.get("phase") == phase and "entropy" in r]
        if phase_data:
            entropies = [r["entropy"] for r in phase_data]
            zones = [r["zone"] for r in phase_data]
            print(f"\n{phase.upper()}:")
            print(f"  Mean entropy: {sum(entropies)/len(entropies):.3f} nats")
            print(f"  Min: {min(entropies):.3f} | Max: {max(entropies):.3f}")
            print(f"  Zones: {Counter(zones)}")

    # Save session state
    state_path = SESSION_DIR / "session_001_state.json"
    state = {
        "session_id": "oracle_session_001",
        "model": MODEL,
        "started": all_results[0].get("timestamp") if all_results else None,
        "completed": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETED",
        "output_count": len([r for r in all_results if "entropy" in r]),
        "error_count": len([r for r in all_results if "error" in r]),
    }
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

    print(f"\n✓ Session state saved to {state_path}")
    print("\nSession 001 complete. Review outputs before generating report.")

if __name__ == "__main__":
    main()
