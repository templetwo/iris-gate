#!/usr/bin/env python3
"""
IRIS Gate Chamber Entropy Measurement
Validates entropy ranges in ceremonial vs analytical chamber responses
"""

import json
import math
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

def shannon_entropy(text):
    """Calculate Shannon entropy of text in nats"""
    tokens = text.split()
    if not tokens:
        return 0.0

    token_counts = Counter(tokens)
    total = len(tokens)

    entropy = 0
    for count in token_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log(p)

    return round(entropy, 3)


def analyze_chamber_responses(session_file):
    """Analyze entropy in chamber responses from a session"""

    with open(session_file, 'r') as f:
        data = json.load(f)

    print("=" * 80)
    print("IRIS GATE CHAMBER ENTROPY ANALYSIS")
    print("=" * 80)
    print(f"\nSession: {session_file}")
    print(f"Date: {data.get('session_metadata', {}).get('timestamp', 'Unknown')}")
    print()

    results = {
        "session_file": str(session_file),
        "timestamp": datetime.utcnow().isoformat(),
        "chambers": [],
        "models": {}
    }

    # Analyze each chamber
    for chamber_name, chamber_data in data.get('chambers', {}).items():
        print(f"\n{'─' * 80}")
        print(f"CHAMBER: {chamber_name}")
        print(f"{'─' * 80}")

        chamber_results = {
            "chamber": chamber_name,
            "prompt_type": chamber_data.get('prompt_type', 'unknown'),
            "prompt_length": len(chamber_data.get('prompt', '').split()),
            "model_entropies": {}
        }

        # Analyze each model's response
        for response_data in chamber_data.get('responses', []):
            model_name = response_data.get('model', 'unknown')
            response = response_data.get('response', '')

            # Skip error responses
            if 'error' in response_data:
                print(f"\n{model_name}: [ERROR - {response_data.get('error', 'unknown')}]")
                continue

            if response:
                entropy = shannon_entropy(response)
                chamber_results["model_entropies"][model_name] = entropy

                print(f"\n{model_name}:")
                print(f"  Entropy: {entropy:.2f} nats")
                print(f"  Response length: {len(response.split())} tokens")
                print(f"  First 100 chars: {response[:100]}...")

        # Calculate chamber statistics
        entropies = list(chamber_results["model_entropies"].values())
        if entropies:
            chamber_results["avg_entropy"] = round(sum(entropies) / len(entropies), 3)
            chamber_results["min_entropy"] = round(min(entropies), 3)
            chamber_results["max_entropy"] = round(max(entropies), 3)

            print(f"\n  Chamber Statistics:")
            print(f"    Average Entropy: {chamber_results['avg_entropy']:.2f} nats")
            print(f"    Range: {chamber_results['min_entropy']:.2f} - {chamber_results['max_entropy']:.2f} nats")

        results["chambers"].append(chamber_results)

    # Model-level analysis
    print(f"\n{'═' * 80}")
    print("MODEL-LEVEL ANALYSIS")
    print(f"{'═' * 80}")

    for chamber_result in results["chambers"]:
        for model_name, entropy in chamber_result["model_entropies"].items():
            if model_name not in results["models"]:
                results["models"][model_name] = {
                    "entropies": [],
                    "chambers": []
                }
            results["models"][model_name]["entropies"].append(entropy)
            results["models"][model_name]["chambers"].append(chamber_result["chamber"])

    for model_name, model_data in results["models"].items():
        avg_entropy = sum(model_data["entropies"]) / len(model_data["entropies"])
        print(f"\n{model_name}:")
        print(f"  Average Entropy: {avg_entropy:.2f} nats")
        print(f"  Range: {min(model_data['entropies']):.2f} - {max(model_data['entropies']):.2f} nats")
        print(f"  Chambers analyzed: {len(model_data['chambers'])}")

    # Cross-protocol comparison
    print(f"\n{'═' * 80}")
    print("CROSS-PROTOCOL COMPARISON")
    print(f"{'═' * 80}")

    all_entropies = []
    for chamber_result in results["chambers"]:
        all_entropies.extend(chamber_result["model_entropies"].values())

    if all_entropies:
        avg_entropy = sum(all_entropies) / len(all_entropies)
        min_entropy = min(all_entropies)
        max_entropy = max(all_entropies)

        print(f"\nIRIS Gate Chamber Responses:")
        print(f"  Average Entropy: {avg_entropy:.2f} nats")
        print(f"  Range: {min_entropy:.2f} - {max_entropy:.2f} nats")
        print(f"\nExpected Ranges (from literature):")
        print(f"  IRIS Gate: 4.2 - 5.8 nats (ceremonial)")
        print(f"  RCT: 3.9 - 5.4 nats (breath cycles)")
        print(f"  RLHF Models: 1.2 - 2.1 nats")

        # Hypothesis test
        if 4.0 <= avg_entropy <= 6.0:
            print(f"\n✓ HYPOTHESIS SUPPORTED: IRIS Gate responses fall within high-entropy zone")
            print(f"  Aligns with RCT findings (3.9-5.4 nats overlap)")
        else:
            print(f"\n⚠ UNEXPECTED: Entropy outside predicted range")

    # Save results
    output_file = session_file.parent / f"{session_file.stem}_entropy_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'═' * 80}")
    print(f"Results saved: {output_file}")
    print(f"{'═' * 80}\n")

    return results


def analyze_all_sessions(investigations_dir="."):
    """Analyze all IRIS Gate session files in a directory"""

    investigations_path = Path(investigations_dir)
    session_files = list(investigations_path.glob("*_session_*.json"))

    if not session_files:
        print(f"No session files found in {investigations_dir}")
        print("Looking for files matching pattern: *_session_*.json")
        return

    print(f"Found {len(session_files)} session file(s)")

    all_results = []
    for session_file in session_files:
        print(f"\n{'═' * 80}")
        print(f"Processing: {session_file.name}")
        print(f"{'═' * 80}")

        try:
            results = analyze_chamber_responses(session_file)
            all_results.append(results)
        except Exception as e:
            print(f"Error processing {session_file}: {e}")
            continue

    # Meta-analysis across all sessions
    if len(all_results) > 1:
        print(f"\n{'═' * 80}")
        print("META-ANALYSIS: All Sessions")
        print(f"{'═' * 80}")

        all_chamber_entropies = []
        for result in all_results:
            for chamber in result["chambers"]:
                all_chamber_entropies.extend(chamber["model_entropies"].values())

        if all_chamber_entropies:
            avg = sum(all_chamber_entropies) / len(all_chamber_entropies)
            print(f"\nAcross {len(all_results)} sessions:")
            print(f"  Total responses analyzed: {len(all_chamber_entropies)}")
            print(f"  Average Entropy: {avg:.2f} nats")
            print(f"  Range: {min(all_chamber_entropies):.2f} - {max(all_chamber_entropies):.2f} nats")

    return all_results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Analyze specific file
        session_file = Path(sys.argv[1])
        if session_file.exists():
            analyze_chamber_responses(session_file)
        else:
            print(f"Error: File not found: {session_file}")
    else:
        # Analyze all sessions in current directory
        analyze_all_sessions(".")
