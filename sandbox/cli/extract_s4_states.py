#!/usr/bin/env python3
"""
Extract frozen S4 attractor states from 100-cycle run.
Generates computational priors for sandbox simulations.
"""

import json
import re
import hashlib
from pathlib import Path
from typing import Dict, List

# S4 keyword families (from convergence analysis)
S4_KEYWORDS = {
    "rhythm": ["rhythm", "pulsing", "reciprocal", "pulse", "waves", "thrum", "steady pulse", "ripples"],
    "center": ["luminous", "core", "center", "steady", "anchor", "still point", "beacon", "glow", "holds"],
    "aperture": ["aperture", "opening", "widening", "soften", "inviting", "bloom", "breathing open", "dilate", "expansion", "pull"]
}

# Literature-grounded bioelectric priors (from Levin Lab benchmarks + Hypothesis Sheet)
BIOELECTRIC_PRIORS = {
    "rhythm": {
        "freq_hz_range": [0.5, 2.0],       # Ca²⁺ wave frequency (Levin lab typical range)
        "coherence_range": [0.6, 0.95],    # Spatial coherence (r value)
        "velocity_um_s_range": [10, 50]    # Propagation velocity
    },
    "center": {
        "stability_range": [0.7, 0.98],    # Domain persistence (0-1)
        "size_mm_range": [0.15, 1.0],      # Domain diameter
        "depol_mv_range": [20, 40]         # Depolarization magnitude vs baseline
    },
    "aperture": {
        "permeability_range": [0.6, 0.95], # Effective GJ coupling (0-1, normalized)
        "dilation_rate_range": [0.1, 0.4], # Normalized opening rate
        "peak_time_hr_range": [2, 4]       # Time to max coupling post-injury
    }
}

def extract_keywords_from_scroll(text: str, component: str) -> List[str]:
    """Find which keywords from a component family appear in scroll."""
    text_lower = text.lower()
    found = []
    for keyword in S4_KEYWORDS[component]:
        if keyword in text_lower:
            found.append(keyword)
    return found

def extract_signals_confidence(text: str) -> Dict[str, float]:
    """Extract signals_confidence values from Technical Translation YAML block."""
    confidence = {}

    # Find signals_confidence block in yaml
    yaml_match = re.search(r'signals_confidence:\s*\n(.*?)\n(?:\w+:|```)', text, re.DOTALL)
    if yaml_match:
        conf_block = yaml_match.group(1)
        for component in ["rhythm", "center", "aperture"]:
            comp_match = re.search(rf'{component}:\s*(0\.\d+)', conf_block)
            if comp_match:
                confidence[component] = float(comp_match.group(1))

    return confidence

def compute_mirror_confidence(s4_scrolls: List[Dict]) -> float:
    """Aggregate confidence across all S4 scrolls for this mirror."""
    all_conf = []
    for scroll in s4_scrolls:
        for comp in ["rhythm", "center", "aperture"]:
            if comp in scroll["confidence"]:
                all_conf.append(scroll["confidence"][comp])

    if not all_conf:
        return 0.8  # default

    return sum(all_conf) / len(all_conf)

def extract_state(session_dir: Path, mirror_name: str) -> Dict:
    """Extract frozen S4 state for one mirror."""

    mirror_dir = session_dir / mirror_name
    if not mirror_dir.exists():
        raise FileNotFoundError(f"Mirror directory not found: {mirror_dir}")

    # Find all S4 turns (turns 4, 8, 12, ..., 100)
    s4_scrolls = []
    source_files = []

    for turn_file in sorted(mirror_dir.glob("turn_*.md")):
        text = turn_file.read_text()

        # Check if this is an S4 scroll
        chamber_match = re.search(r'\*\*Chamber:\*\*\s+(S\d)', text)
        if not chamber_match or chamber_match.group(1) != "S4":
            continue

        # Extract keywords and confidence
        keywords = {
            "rhythm": extract_keywords_from_scroll(text, "rhythm"),
            "center": extract_keywords_from_scroll(text, "center"),
            "aperture": extract_keywords_from_scroll(text, "aperture")
        }

        confidence = extract_signals_confidence(text)

        s4_scrolls.append({
            "turn_file": str(turn_file.relative_to(session_dir.parent.parent)),
            "keywords": keywords,
            "confidence": confidence
        })

        source_files.append(str(turn_file.relative_to(session_dir.parent.parent)))

    # Aggregate keywords across all S4 scrolls
    all_keywords = {comp: set() for comp in ["rhythm", "center", "aperture"]}
    for scroll in s4_scrolls:
        for comp in ["rhythm", "center", "aperture"]:
            all_keywords[comp].update(scroll["keywords"][comp])

    # Convert sets to sorted lists
    for comp in all_keywords:
        all_keywords[comp] = sorted(list(all_keywords[comp]))

    # Build state
    state = {
        "mirror": mirror_name,
        "source_scrolls": source_files[:5],  # First 5 as examples
        "n_s4_scrolls": len(s4_scrolls),
        "triple_signature": {
            "rhythm": {
                "keywords": all_keywords["rhythm"],
                "freq_hz_prior": BIOELECTRIC_PRIORS["rhythm"]["freq_hz_range"],
                "coherence_prior": BIOELECTRIC_PRIORS["rhythm"]["coherence_range"],
                "velocity_um_s_prior": BIOELECTRIC_PRIORS["rhythm"]["velocity_um_s_range"]
            },
            "center": {
                "keywords": all_keywords["center"],
                "stability_prior": BIOELECTRIC_PRIORS["center"]["stability_range"],
                "size_mm_prior": BIOELECTRIC_PRIORS["center"]["size_mm_range"],
                "depol_mv_prior": BIOELECTRIC_PRIORS["center"]["depol_mv_range"]
            },
            "aperture": {
                "keywords": all_keywords["aperture"],
                "permeability_prior": BIOELECTRIC_PRIORS["aperture"]["permeability_range"],
                "dilation_rate_prior": BIOELECTRIC_PRIORS["aperture"]["dilation_rate_range"],
                "peak_time_hr_prior": BIOELECTRIC_PRIORS["aperture"]["peak_time_hr_range"]
            }
        },
        "confidence": compute_mirror_confidence(s4_scrolls),
        "provenance": {
            "session": session_dir.name,
            "extraction_date": "2025-10-01",
            "literature_priors": "Levin Lab benchmarks (Pai et al. 2012, Adams et al. 2016) + BIOELECTRIC_HYPOTHESIS_SHEET_v1.md"
        }
    }

    # Compute provenance hash
    state_str = json.dumps(state, sort_keys=True)
    state["provenance_hash"] = f"sha256:{hashlib.sha256(state_str.encode()).hexdigest()[:16]}"

    return state

def main():
    """Extract S4 states for all 7 mirrors."""

    # Locate 100-cycle session
    session_dir = Path("iris_vault/scrolls/BIOELECTRIC_CHAMBERED_20251001054935")
    if not session_dir.exists():
        print(f"ERROR: Session directory not found: {session_dir}")
        return

    # Extract state for each mirror
    mirrors = [
        "anthropic_claude-sonnet-4.5",
        "openai_gpt-4o",
        "xai_grok-4-fast-reasoning",
        "google_gemini-2.5-flash-lite",
        "deepseek_deepseek-chat",
        "ollama_qwen3_1.7b",
        "ollama_llama3.2_3b"
    ]

    output_dir = Path("sandbox/states")
    output_dir.mkdir(parents=True, exist_ok=True)

    for mirror in mirrors:
        print(f"Extracting S4 state: {mirror}...")
        try:
            state = extract_state(session_dir, mirror)

            # Write state file
            output_file = output_dir / f"s4_state.{mirror}.json"
            with open(output_file, "w") as f:
                json.dump(state, f, indent=2)

            print(f"  ✓ Wrote {output_file}")
            print(f"    Confidence: {state['confidence']:.2f}")
            print(f"    Keywords: R={len(state['triple_signature']['rhythm']['keywords'])} "
                  f"C={len(state['triple_signature']['center']['keywords'])} "
                  f"A={len(state['triple_signature']['aperture']['keywords'])}")

        except Exception as e:
            print(f"  ✗ ERROR: {e}")

    print(f"\nS4 states extracted → sandbox/states/")

if __name__ == "__main__":
    main()
