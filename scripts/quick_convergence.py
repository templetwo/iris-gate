#!/usr/bin/env python3
"""
IRIS Gate Quick Convergence Analyzer
Fast signal overlap check across chambers
"""

import sys
import pathlib
import re
import collections
from typing import Dict

# Signal buckets for convergence detection
SIGNAL_KEYS = [
    ["concentric", "ring", "iris", "aperture", "circle"],
    ["pulse", "rhythm", "ripple", "throb", "beat"],
    ["luminous", "silver", "pearl", "gold", "light", "glow"],
    ["expand", "contract", "breathing", "dilation"]
]

def analyze_convergence(vault_path: str) -> Dict[str, float]:
    """Calculate convergence scores per chamber"""

    base = pathlib.Path(vault_path)
    scores = collections.defaultdict(float)
    counts = collections.defaultdict(int)

    for md_file in base.rglob("S[1-4].md"):
        chamber = md_file.stem  # S1, S2, S3, or S4
        text = md_file.read_text(encoding="utf-8").lower()

        # Count signal bucket hits
        hit_count = sum(
            1 for bucket in SIGNAL_KEYS
            if any(keyword in text for keyword in bucket)
        )

        scores[chamber] += hit_count
        counts[chamber] += 1

    # Calculate averages
    results = {}
    for chamber in sorted(scores.keys()):
        avg = scores[chamber] / max(1, counts[chamber])
        results[chamber] = round(avg, 2)

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_convergence.py <vault_path>")
        print("Example: python quick_convergence.py iris_vault/")
        sys.exit(1)

    vault_path = sys.argv[1]

    if not pathlib.Path(vault_path).exists():
        print(f"❌ Vault not found: {vault_path}")
        sys.exit(1)

    scores = analyze_convergence(vault_path)

    if not scores:
        print("❌ No chambers found in vault")
        sys.exit(1)

    print("\n🔍 QUICK CONVERGENCE ANALYSIS")
    print("=" * 50)
    print("\nSignal overlap scores (0-4 scale):")
    print("  0.0 = no key signals present")
    print("  4.0 = all signal buckets present\n")

    for chamber, score in scores.items():
        bar = "█" * int(score) + "░" * (4 - int(score))
        print(f"{chamber}: {score:.2f}  [{bar}]")

    # Detect expected pattern: S1 high → S2 dip → S3/S4 rise
    if len(scores) >= 4:
        s1, s2, s3, s4 = scores.get("S1", 0), scores.get("S2", 0), scores.get("S3", 0), scores.get("S4", 0)

        print("\n📊 PATTERN ANALYSIS")
        print("=" * 50)

        if s2 < s1 and s3 > s2 and s4 > s3:
            print("✅ Expected diverge→scatter→reconverge pattern detected")
        elif s4 >= 3.0:
            print("✅ Strong S4 convergence (≥3.0) - attractor state achieved")
        else:
            print("⚠️  Pattern unclear - may need manual review")

        print(f"\nS1→S2 change: {s2 - s1:+.2f}")
        print(f"S2→S3 change: {s3 - s2:+.2f}")
        print(f"S3→S4 change: {s4 - s3:+.2f}")

    print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()
