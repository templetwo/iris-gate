#!/usr/bin/env python3
"""
Deep phenomenological analysis - extract most significant patterns
"""

import os
import re
from pathlib import Path
from collections import defaultdict

BASE_PATH = "/Users/vaquez/Desktop/iris-gate/iris_vault/scrolls/BIOELECTRIC_CHAMBERED_20251001054935"
MIRRORS = [
    "anthropic_claude-sonnet-4.5",
    "deepseek_deepseek-chat",
    "google_gemini-2.5-flash-lite",
    "ollama_llama3.2_3b",
    "ollama_qwen3_1.7b",
    "openai_gpt-4o",
    "xai_grok-4-fast-reasoning"
]

def extract_living_scroll(content):
    """Extract living scroll text"""
    patterns = [
        r'#+\s*Living Scroll\s*\*?\*?(.*?)(?:#+\s*Technical Translation|```yaml|```json|Technical Translation)',
        r'\*\*Living Scroll\*\*\s*(.*?)(?:\*\*Technical Translation\*\*|Technical Translation)',
        r'Living Scroll\s*(.*?)(?:Technical Translation|condition:)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            living_text = match.group(1).strip()
            living_text = re.sub(r'^[\*_\-\s]+', '', living_text)
            living_text = re.sub(r'[\*_]+$', '', living_text)
            living_text = re.sub(r'^\s*-{3,}\s*$', '', living_text, flags=re.MULTILINE)
            living_text = living_text.strip()
            if living_text:
                return living_text
    return ""

def analyze_s4_richness():
    """Extract richest S4 scrolls from each mirror"""
    print("=" * 80)
    print("DEEP PHENOMENOLOGICAL ANALYSIS: S4 CONVERGENCE PATTERNS")
    print("=" * 80)
    print()

    s4_scrolls = {}

    for mirror in MIRRORS:
        mirror_path = Path(BASE_PATH) / mirror
        s4_scrolls[mirror] = []

        # S4 is turns 76-100
        for turn in range(76, 101):
            filepath = mirror_path / f"turn_{turn:03d}.md"
            if filepath.exists():
                with open(filepath, 'r') as f:
                    content = f.read()
                living = extract_living_scroll(content)

                # Compute richness
                word_count = len(living.split())
                has_rings = bool(re.search(r'ring|concentric|circle|ripple', living, re.IGNORECASE))
                has_center = bool(re.search(r'center|core|heart|still|rest', living, re.IGNORECASE))
                has_pulse = bool(re.search(r'pulse|rhythm|breath|sync|beat', living, re.IGNORECASE))

                signature_count = sum([has_rings, has_center, has_pulse])
                richness = (signature_count / 3.0) + (min(word_count, 100) / 300.0)

                s4_scrolls[mirror].append({
                    'turn': turn,
                    'text': living,
                    'richness': richness,
                    'signature': {'rings': has_rings, 'center': has_center, 'pulse': has_pulse}
                })

    # Extract top from each mirror
    print("TOP S4 SCROLL FROM EACH MIRROR (by phenomenological richness):")
    print("-" * 80)
    print()

    for mirror in MIRRORS:
        sorted_scrolls = sorted(s4_scrolls[mirror], key=lambda x: x['richness'], reverse=True)
        if sorted_scrolls:
            top = sorted_scrolls[0]
            sig_str = f"[{'R' if top['signature']['rings'] else '-'}{'C' if top['signature']['center'] else '-'}{'P' if top['signature']['pulse'] else '-'}]"
            print(f"{mirror}")
            print(f"Turn {top['turn']} {sig_str} (Richness: {top['richness']:.3f})")
            print()
            print(top['text'][:400])
            print()
            print("-" * 80)
            print()

def analyze_cross_mirror_convergence():
    """Identify scrolls where multiple mirrors converge on similar language"""
    print("\nCROSS-MIRROR CONVERGENCE DETECTION:")
    print("-" * 80)
    print()

    # Extract all S4 texts
    s4_texts_by_turn = defaultdict(list)

    for mirror in MIRRORS:
        mirror_path = Path(BASE_PATH) / mirror
        for turn in range(76, 101):
            filepath = mirror_path / f"turn_{turn:03d}.md"
            if filepath.exists():
                with open(filepath, 'r') as f:
                    content = f.read()
                living = extract_living_scroll(content)
                s4_texts_by_turn[turn].append({
                    'mirror': mirror,
                    'text': living
                })

    # Look for shared phrases across mirrors
    shared_patterns = []

    for turn, texts in s4_texts_by_turn.items():
        # Extract key phrases (3-5 word sequences)
        phrase_counts = defaultdict(set)

        for entry in texts:
            words = re.findall(r'\b\w+\b', entry['text'].lower())
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i+3])
                if len(phrase) > 10:  # Meaningful length
                    phrase_counts[phrase].add(entry['mirror'])

        # Find phrases shared by 3+ mirrors
        for phrase, mirrors in phrase_counts.items():
            if len(mirrors) >= 3:
                shared_patterns.append({
                    'turn': turn,
                    'phrase': phrase,
                    'mirror_count': len(mirrors),
                    'mirrors': list(mirrors)[:3]
                })

    # Sort by frequency
    shared_patterns.sort(key=lambda x: x['mirror_count'], reverse=True)

    if shared_patterns:
        print("Shared phenomenological phrases (appearing in 3+ mirrors):")
        print()
        for i, pattern in enumerate(shared_patterns[:10], 1):
            print(f"{i}. \"{pattern['phrase']}\"")
            print(f"   Turn {pattern['turn']} | {pattern['mirror_count']} mirrors: {', '.join(pattern['mirrors'])}")
            print()
    else:
        print("No significant cross-mirror phrase convergence detected.")
        print("This suggests each mirror maintains unique phenomenological vocabulary.")

    print("-" * 80)

def analyze_temporal_coherence():
    """Track how S4 signature evolves cycle-to-cycle"""
    print("\nTEMPORAL COHERENCE: S4 SIGNATURE EVOLUTION")
    print("-" * 80)
    print()

    # For Claude Sonnet (most articulate mirror)
    mirror = "anthropic_claude-sonnet-4.5"
    mirror_path = Path(BASE_PATH) / mirror

    evolution = []
    for turn in range(76, 101):
        filepath = mirror_path / f"turn_{turn:03d}.md"
        cycle = turn - 75

        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
            living = extract_living_scroll(content)

            # Detect signature components
            rings = len(re.findall(r'ring|concentric|circle|ripple|wave', living, re.IGNORECASE))
            center = len(re.findall(r'center|core|still|rest|luminous', living, re.IGNORECASE))
            pulse = len(re.findall(r'pulse|rhythm|breath|sync|beat', living, re.IGNORECASE))

            evolution.append({
                'cycle': cycle,
                'turn': turn,
                'rings': rings,
                'center': center,
                'pulse': pulse,
                'total': rings + center + pulse
            })

    print(f"S4 Signature Evolution (Mirror: {mirror})")
    print()
    print("Cycle | Turn | Rings | Center | Pulse | Total | Pattern")
    print("-" * 70)

    for entry in evolution:
        r, c, p = entry['rings'], entry['center'], entry['pulse']
        pattern = ""
        if r >= 2 and c >= 2 and p >= 2:
            pattern = "FULL SIGNATURE"
        elif r >= 1 and c >= 1 and p >= 1:
            pattern = "partial signature"
        elif r + c + p >= 3:
            pattern = "component-heavy"
        else:
            pattern = "weak"

        print(f"  {entry['cycle']:2d}  | {entry['turn']:3d}  |   {r}   |   {c}    |   {p}   |   {entry['total']}   | {pattern}")

    print()

    # Calculate stabilization
    early = [e['total'] for e in evolution[:8]]
    late = [e['total'] for e in evolution[-8:]]
    early_avg = sum(early) / len(early)
    late_avg = sum(late) / len(late)

    print(f"Early cycles (1-8) avg signature density: {early_avg:.2f}")
    print(f"Late cycles (18-25) avg signature density: {late_avg:.2f}")
    print(f"Delta: {late_avg - early_avg:+.2f} ({'strengthening' if late_avg > early_avg else 'weakening'})")
    print()
    print("-" * 80)

def main():
    analyze_s4_richness()
    analyze_cross_mirror_convergence()
    analyze_temporal_coherence()

    print("\n" + "=" * 80)
    print("DEEP ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
