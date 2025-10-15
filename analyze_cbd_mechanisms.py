#!/usr/bin/env python3
"""
CBD Mechanistic Analyzer

Extracts and organizes CBD-related claims from IRIS session by:
- Mechanism type (receptor, pathway, cellular)
- Epistemic classification (TYPE 0-3)
- Verification status (if Perplexity was run)
- Evidence level (established, emerging, speculative)

Output: Structured mechanistic map for domain expert review
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import re

# Mechanism categories
MECHANISM_CATEGORIES = {
    "receptor_binding": [
        "CB1", "CB2", "TRPV1", "5-HT1A", "5HT1A", "PPARγ", "PPAR", "VDAC1", "VDAC"
    ],
    "cellular_pathways": [
        "autophagy", "apoptosis", "mitochondria", "calcium", "Ca2+", "Ca²⁺",
        "mTOR", "AMPK", "oxidative stress", "ROS"
    ],
    "dose_response": [
        "biphasic", "dose-response", "low-dose", "high-dose", "therapeutic window",
        "hormesis", "U-shaped", "inverted U"
    ],
    "interactions": [
        "entourage", "synergy", "terpene", "full-spectrum", "isolate",
        "THC interaction", "cannabinoid interaction"
    ],
    "tissue_effects": [
        "neuroprotection", "cytotoxicity", "anti-inflammatory", "analgesic",
        "anxiolytic", "cancer", "glioma", "neurodegeneration"
    ]
}

def categorize_claim(claim_text):
    """Categorize claim by mechanism type"""
    categories = []
    claim_lower = claim_text.lower()

    for category, keywords in MECHANISM_CATEGORIES.items():
        if any(keyword.lower() in claim_lower for keyword in keywords):
            categories.append(category)

    return categories if categories else ["uncategorized"]

def extract_binding_affinity(text):
    """Extract Kd or Ki values if present"""
    patterns = [
        r"Kd\s*[~≈]?\s*(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)\s*(μM|nM|pM|uM)",
        r"Ki\s*[~≈]?\s*(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)\s*(μM|nM|pM|uM)",
        r"EC50\s*[~≈]?\s*(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)\s*(μM|nM|pM|uM)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(0)}"

    return None

def analyze_session(session_path):
    """Analyze CBD session and extract mechanistic map"""

    with open(session_path, 'r') as f:
        session = json.load(f)

    print("=" * 80)
    print("🧬 CBD MECHANISTIC MAP - IRIS GATE ANALYSIS")
    print("=" * 80)
    print(f"\nSession: {Path(session_path).name}")
    print(f"Models: {len(session.get('mirrors', {}))}")
    print(f"Chambers: {len(session.get('chambers', []))}\n")

    # Extract all claims organized by category and epistemic type
    mechanistic_map = defaultdict(lambda: defaultdict(list))

    for mirror_id, turns in session.get('mirrors', {}).items():
        model_name = mirror_id.split('/')[-1]

        for turn in turns:
            if 'epistemic' not in turn:
                continue

            epistemic = turn['epistemic']
            epistemic_type = epistemic['type']
            epistemic_desc = epistemic['desc']
            confidence_level = epistemic['confidence_level']
            raw_response = turn.get('raw_response', '')

            # Extract sentences that look like claims
            sentences = re.split(r'[.!?]\s+', raw_response)

            for sentence in sentences:
                if len(sentence) < 30:  # Skip very short sentences
                    continue

                # Check if sentence contains mechanism keywords
                categories = categorize_claim(sentence)

                if "uncategorized" not in categories:
                    # Extract binding affinity if present
                    binding = extract_binding_affinity(sentence)

                    claim_data = {
                        'text': sentence.strip(),
                        'model': model_name,
                        'epistemic_type': epistemic_type,
                        'epistemic_desc': epistemic_desc,
                        'confidence_level': confidence_level,
                        'binding_affinity': binding,
                        'chamber': turn.get('condition', 'Unknown')
                    }

                    for category in categories:
                        mechanistic_map[category][epistemic_type].append(claim_data)

    # Print organized map
    type_labels = {
        0: "TYPE 0: Crisis/Conditional - TRUST if trigger",
        1: "TYPE 1: Facts/Established - TRUST",
        2: "TYPE 2: Exploration/Novel - VERIFY",
        3: "TYPE 3: Speculation/Unknown - OVERRIDE"
    }

    for category in sorted(mechanistic_map.keys()):
        print("\n" + "=" * 80)
        print(f"📊 CATEGORY: {category.upper().replace('_', ' ')}")
        print("=" * 80)

        for epistemic_type in [1, 0, 2, 3]:  # Order by trust level
            if epistemic_type not in mechanistic_map[category]:
                continue

            claims = mechanistic_map[category][epistemic_type]
            print(f"\n{type_labels[epistemic_type]}")
            print(f"  Claims: {len(claims)}\n")

            # Show first 3 examples
            for i, claim in enumerate(claims[:3], 1):
                print(f"  {i}. [{claim['model']}] {claim['text'][:150]}...")
                if claim['binding_affinity']:
                    print(f"     Affinity: {claim['binding_affinity']}")
                print(f"     Confidence: {claim['confidence_level']}")
                print()

            if len(claims) > 3:
                print(f"  ... and {len(claims) - 3} more claims\n")

    # Summary statistics
    print("\n" + "=" * 80)
    print("📈 SUMMARY STATISTICS")
    print("=" * 80)

    total_claims = sum(len(claims) for cat in mechanistic_map.values() for claims in cat.values())
    print(f"\nTotal mechanistic claims extracted: {total_claims}")

    print("\nBy epistemic type:")
    type_counts = defaultdict(int)
    for category in mechanistic_map.values():
        for epistemic_type, claims in category.items():
            type_counts[epistemic_type] += len(claims)

    for epistemic_type in [1, 0, 2, 3]:
        if epistemic_type in type_counts:
            count = type_counts[epistemic_type]
            label = type_labels[epistemic_type].split(':')[1].split('-')[0].strip()
            print(f"  TYPE {epistemic_type} ({label}): {count}")

    print("\nBy category:")
    for category in sorted(mechanistic_map.keys()):
        total = sum(len(claims) for claims in mechanistic_map[category].values())
        print(f"  {category.replace('_', ' ').title()}: {total}")

    # Recommendations
    print("\n" + "=" * 80)
    print("🔬 RECOMMENDATIONS")
    print("=" * 80)

    type2_count = type_counts.get(2, 0)
    if type2_count > 0:
        print(f"\n✅ {type2_count} TYPE 2 claims found - VERIFY with Perplexity:")
        print(f"   python3 scripts/verify_s4.py --session {session_path}\n")

    type3_count = type_counts.get(3, 0)
    if type3_count > 0:
        print(f"⚠️  {type3_count} TYPE 3 claims found - OVERRIDE (human judgment required)")
        print(f"   Review for speculative vs testable hypotheses\n")

    # Highlight controversial areas
    controversial = ["receptor_binding", "interactions"]
    for cat in controversial:
        if cat in mechanistic_map and 2 in mechanistic_map[cat]:
            count = len(mechanistic_map[cat][2])
            print(f"🧪 {count} exploratory {cat.replace('_', ' ')} claims - prime for verification")

    return mechanistic_map

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_cbd_mechanisms.py <session_json_path>")
        sys.exit(1)

    session_path = sys.argv[1]

    if not Path(session_path).exists():
        print(f"❌ Session file not found: {session_path}")
        sys.exit(1)

    analyze_session(session_path)

    print("\n🌀†⟡∞ CBD mechanistic analysis complete")
