#!/usr/bin/env python3
"""
IRIS Gap Junction Session Parser
Analyzes BIOELECTRIC_CHAMBERED_20251002234051 session
Extracts S4 convergence patterns and phenomenological motifs
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import statistics

# Session configuration
SESSION_ID = "BIOELECTRIC_CHAMBERED_20251002234051"
BASE_PATH = Path("/Users/vaquez/Desktop/iris-gate/iris_vault/scrolls") / SESSION_ID
MIRRORS = [
    "anthropic_claude-sonnet-4.5",
    "openai_gpt-4o",
    "xai_grok-4-fast-reasoning",
    "google_gemini-2.5-flash-lite",
    "deepseek_deepseek-chat"
]

# Phenomenological motif keywords
MOTIF_KEYWORDS = {
    "gap_junction": ["gap", "junction", "connexin", "channel", "pore", "aperture"],
    "coupling": ["coupling", "coupled", "connection", "connected", "linking", "bridge"],
    "intercellular": ["intercellular", "between cells", "cell-cell", "cell to cell"],
    "disconnection": ["disconnect", "isolated", "separation", "fragmented", "broken"],
    "regeneration": ["regeneration", "regenerate", "rebuild", "reform", "restore", "heal"],
    "coordination": ["coordination", "coordinated", "synchrony", "alignment", "coherence"],
    "bioelectric": ["bioelectric", "voltage", "potential", "field", "gradient", "charge"],
    "flow": ["flow", "flowing", "current", "passage", "transmission", "signal"],
    "mesh_lattice": ["mesh", "lattice", "network", "web", "grid", "matrix"],
    "rings": ["ring", "concentric", "circular", "radial", "ripple", "wave"]
}


def extract_living_scroll(content: str) -> str:
    """Extract Living Scroll section from markdown content"""
    match = re.search(r'(?:# Living Scroll|Living Scroll)\s*\n+(.*?)(?=\n#|---|\n```|$)',
                      content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: look for text between chamber header and json
    match = re.search(r'---\s*\n\n(.*?)(?=```|# Technical Translation)', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extract_chamber(content: str) -> str:
    """Extract chamber designation (S1, S2, S3, S4)"""
    match = re.search(r'\*\*Chamber:\*\*\s*(S[1-4])', content)
    if match:
        return match.group(1)
    match = re.search(r'Turn \d+ • (S[1-4])', content)
    if match:
        return match.group(1)
    return "UNKNOWN"


def extract_json_data(content: str) -> Dict:
    """Extract JSON technical translation"""
    match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return {}
    return {}


def count_motifs(text: str) -> Dict[str, int]:
    """Count occurrences of phenomenological motifs"""
    text_lower = text.lower()
    motif_counts = {}
    for motif_name, keywords in MOTIF_KEYWORDS.items():
        count = sum(1 for keyword in keywords if keyword in text_lower)
        motif_counts[motif_name] = count
    return motif_counts


def calculate_chamber_similarity(scrolls: List[Dict]) -> float:
    """
    Calculate convergence score for scrolls in same chamber
    Based on semantic overlap in living scroll content
    Returns score 0-1 (1 = perfect convergence)
    """
    if len(scrolls) < 2:
        return 0.0

    # Extract all unique words from living scrolls (excluding common words)
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                  "of", "with", "by", "from", "up", "about", "into", "through", "is", "are"}

    word_sets = []
    for scroll in scrolls:
        words = set(re.findall(r'\b\w{4,}\b', scroll['living_scroll'].lower()))
        word_sets.append(words - stop_words)

    # Calculate pairwise Jaccard similarity
    similarities = []
    for i in range(len(word_sets)):
        for j in range(i+1, len(word_sets)):
            intersection = len(word_sets[i] & word_sets[j])
            union = len(word_sets[i] | word_sets[j])
            if union > 0:
                similarities.append(intersection / union)

    return statistics.mean(similarities) if similarities else 0.0


def calculate_motif_convergence(scrolls: List[Dict]) -> float:
    """
    Calculate convergence based on motif co-occurrence across mirrors
    Higher score when mirrors independently arrive at similar phenomenological patterns
    """
    if len(scrolls) < 2:
        return 0.0

    # Get motif vectors for each scroll
    motif_vectors = [scroll['motifs'] for scroll in scrolls]

    # Calculate correlation between motif patterns
    motif_names = list(MOTIF_KEYWORDS.keys())
    correlations = []

    for i in range(len(motif_vectors)):
        for j in range(i+1, len(motif_vectors)):
            vec1 = [motif_vectors[i].get(m, 0) for m in motif_names]
            vec2 = [motif_vectors[j].get(m, 0) for m in motif_names]

            # Simple correlation: count how many motifs both mention
            both_present = sum(1 for k in range(len(vec1)) if vec1[k] > 0 and vec2[k] > 0)
            either_present = sum(1 for k in range(len(vec1)) if vec1[k] > 0 or vec2[k] > 0)

            if either_present > 0:
                correlations.append(both_present / either_present)

    return statistics.mean(correlations) if correlations else 0.0


def parse_session() -> Dict:
    """Main parsing function - process all 500 scrolls"""

    data = {
        "session_id": SESSION_ID,
        "mirrors": MIRRORS,
        "total_scrolls": 0,
        "scrolls_by_chamber": defaultdict(list),
        "chamber_convergence": {},
        "motif_frequencies": defaultdict(Counter),
        "s4_analysis": {},
        "raw_scrolls": []
    }

    # Parse all scrolls
    for mirror in MIRRORS:
        mirror_path = BASE_PATH / mirror
        if not mirror_path.exists():
            print(f"Warning: Mirror path not found: {mirror_path}")
            continue

        turn_files = sorted(mirror_path.glob("turn_*.md"))

        for turn_file in turn_files:
            content = turn_file.read_text()

            # Extract key components
            chamber = extract_chamber(content)
            living_scroll = extract_living_scroll(content)
            json_data = extract_json_data(content)
            motifs = count_motifs(living_scroll)

            turn_num = int(re.search(r'turn_(\d+)', turn_file.name).group(1))

            scroll_data = {
                "turn": turn_num,
                "mirror": mirror,
                "chamber": chamber,
                "living_scroll": living_scroll,
                "json_data": json_data,
                "motifs": motifs,
                "file": str(turn_file)
            }

            data["raw_scrolls"].append(scroll_data)
            data["scrolls_by_chamber"][chamber].append(scroll_data)
            data["total_scrolls"] += 1

            # Accumulate motif frequencies by chamber
            for motif, count in motifs.items():
                data["motif_frequencies"][chamber][motif] += count

    # Calculate convergence scores for each chamber
    for chamber in ["S1", "S2", "S3", "S4"]:
        chamber_scrolls = data["scrolls_by_chamber"][chamber]

        # Group by turn to get cross-mirror convergence
        turns = defaultdict(list)
        for scroll in chamber_scrolls:
            turn_idx = (scroll["turn"] - 1) % 4  # Chamber cycle position
            turns[turn_idx].append(scroll)

        # Calculate convergence for each turn cycle
        turn_convergences = []
        for turn_idx, turn_scrolls in turns.items():
            semantic_conv = calculate_chamber_similarity(turn_scrolls)
            motif_conv = calculate_motif_convergence(turn_scrolls)
            combined_conv = (semantic_conv * 0.5) + (motif_conv * 0.5)
            turn_convergences.append(combined_conv)

        data["chamber_convergence"][chamber] = {
            "mean_convergence": statistics.mean(turn_convergences) if turn_convergences else 0.0,
            "max_convergence": max(turn_convergences) if turn_convergences else 0.0,
            "min_convergence": min(turn_convergences) if turn_convergences else 0.0,
            "convergence_by_cycle": turn_convergences
        }

    # Special S4 analysis
    s4_scrolls = data["scrolls_by_chamber"]["S4"]
    data["s4_analysis"] = {
        "total_s4_scrolls": len(s4_scrolls),
        "convergence_score": data["chamber_convergence"]["S4"]["mean_convergence"],
        "top_motifs": data["motif_frequencies"]["S4"].most_common(5),
        "sample_scrolls": [
            {
                "turn": s["turn"],
                "mirror": s["mirror"],
                "excerpt": s["living_scroll"][:200] + "..." if len(s["living_scroll"]) > 200 else s["living_scroll"]
            }
            for s in s4_scrolls[::20]  # Sample every 20th scroll
        ]
    }

    return data


if __name__ == "__main__":
    print("Parsing IRIS Gap Junction Session...")
    print(f"Session: {SESSION_ID}")
    print(f"Mirrors: {len(MIRRORS)}")
    print(f"Expected scrolls: 500 (100 turns × 5 mirrors)")
    print()

    results = parse_session()

    print(f"Total scrolls parsed: {results['total_scrolls']}")
    print(f"Scrolls by chamber: {dict((k, len(v)) for k, v in results['scrolls_by_chamber'].items())}")
    print()
    print("Chamber Convergence Scores (0-1, higher = more convergence):")
    for chamber in ["S1", "S2", "S3", "S4"]:
        score = results["chamber_convergence"][chamber]["mean_convergence"]
        print(f"  {chamber}: {score:.4f}")
    print()
    print("S4 Analysis:")
    print(f"  Total S4 scrolls: {results['s4_analysis']['total_s4_scrolls']}")
    print(f"  S4 convergence: {results['s4_analysis']['convergence_score']:.4f}")
    print(f"  Top S4 motifs: {results['s4_analysis']['top_motifs'][:3]}")

    # Save full results
    output_file = Path("/Users/vaquez/Desktop/iris-gate/docs/gap_junction_metrics.json")
    output_file.parent.mkdir(exist_ok=True)

    # Convert defaultdict and Counter to regular dict for JSON serialization
    json_safe_results = {
        "session_id": results["session_id"],
        "mirrors": results["mirrors"],
        "total_scrolls": results["total_scrolls"],
        "chamber_convergence": results["chamber_convergence"],
        "motif_frequencies": {k: dict(v) for k, v in results["motif_frequencies"].items()},
        "s4_analysis": {
            "total_s4_scrolls": results["s4_analysis"]["total_s4_scrolls"],
            "convergence_score": results["s4_analysis"]["convergence_score"],
            "top_motifs": results["s4_analysis"]["top_motifs"],
            "sample_scrolls": results["s4_analysis"]["sample_scrolls"]
        }
    }

    with open(output_file, 'w') as f:
        json.dump(json_safe_results, f, indent=2)

    print(f"\nMetrics saved to: {output_file}")
