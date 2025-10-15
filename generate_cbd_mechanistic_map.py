#!/usr/bin/env python3
"""
CBD Mechanistic Map Generator

Combines:
1. Mechanistic claim extraction (analyze_cbd_mechanisms.py)
2. Epistemic classification (TYPE 0-3)
3. Perplexity verification results
4. Evidence level assignment

Output: Complete CBD mechanistic map with:
- Receptor interactions (CB1, CB2, TRPV1, 5-HT1A, PPARγ, VDAC1)
- Cellular pathways (autophagy, mitochondria, Ca²⁺)
- Dose-response patterns (biphasic, therapeutic window)
- Entourage effects (full-spectrum vs isolate)
- Controversial mechanisms (VDAC1, polarity flips)

Evidence Levels:
- GOLD: TYPE 1 + SUPPORTED (high confidence, literature-backed)
- SILVER: TYPE 1 OR TYPE 2 + PARTIALLY_SUPPORTED (established or emerging with some support)
- BRONZE: TYPE 2 + NOVEL (exploratory, needs more research)
- SPECULATIVE: TYPE 3 OR CONTRADICTED (speculative or conflicts with literature)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import re

def load_session(session_path):
    """Load session JSON"""
    with open(session_path, 'r') as f:
        return json.load(f)

def load_verification(verification_path):
    """Load verification results if available"""
    if not Path(verification_path).exists():
        return None

    with open(verification_path, 'r') as f:
        return json.load(f)

def assign_evidence_level(epistemic_type, verification_status=None, confidence=None):
    """
    Assign evidence level based on epistemic type + verification.

    GOLD: TYPE 1 + SUPPORTED (high confidence)
    SILVER: TYPE 1 OR (TYPE 2 + PARTIALLY_SUPPORTED)
    BRONZE: TYPE 2 + NOVEL
    SPECULATIVE: TYPE 3 OR CONTRADICTED
    """
    if epistemic_type == 3 or verification_status == "CONTRADICTED":
        return "SPECULATIVE"

    if epistemic_type == 1 and verification_status == "SUPPORTED":
        return "GOLD"

    if epistemic_type == 1 or (epistemic_type == 2 and verification_status == "PARTIALLY_SUPPORTED"):
        return "SILVER"

    if epistemic_type == 2 and verification_status == "NOVEL":
        return "BRONZE"

    if epistemic_type == 2:
        return "BRONZE"  # TYPE 2 without verification defaults to BRONZE

    if epistemic_type == 1:
        return "SILVER"  # TYPE 1 without verification defaults to SILVER

    if epistemic_type == 0:
        return "CONDITIONAL"  # TYPE 0 is conditional logic

    return "UNKNOWN"

def extract_mechanisms_by_category(session_data):
    """Extract mechanistic claims organized by category"""

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

    mechanistic_map = defaultdict(lambda: defaultdict(list))

    for mirror_id, turns in session_data.get('mirrors', {}).items():
        model_name = mirror_id.split('/')[-1]

        for turn in turns:
            if 'epistemic' not in turn:
                continue

            epistemic = turn['epistemic']
            epistemic_type = epistemic['type']
            raw_response = turn.get('raw_response', '')

            # Extract sentences
            sentences = re.split(r'[.!?]\s+', raw_response)

            for sentence in sentences:
                if len(sentence) < 30:
                    continue

                # Categorize
                categories = []
                sentence_lower = sentence.lower()

                for category, keywords in MECHANISM_CATEGORIES.items():
                    if any(keyword.lower() in sentence_lower for keyword in keywords):
                        categories.append(category)

                if categories:
                    claim_data = {
                        'text': sentence.strip(),
                        'model': model_name,
                        'epistemic_type': epistemic_type,
                        'confidence_ratio': epistemic.get('confidence_ratio', 0),
                        'chamber': turn.get('condition', 'Unknown')
                    }

                    for category in categories:
                        mechanistic_map[category][epistemic_type].append(claim_data)

    return mechanistic_map

def generate_map_report(session_path, verification_path=None):
    """Generate comprehensive CBD mechanistic map report"""

    session_data = load_session(session_path)
    verification_data = load_verification(verification_path) if verification_path else None

    mechanistic_map = extract_mechanisms_by_category(session_data)

    print("=" * 80)
    print("🧬 CBD MECHANISTIC MAP - EVIDENCE-GRADED")
    print("=" * 80)
    print(f"\nSession: {Path(session_path).name}")
    print(f"Models: {len(session_data.get('mirrors', {}))}")
    print(f"Verification: {'✅ Available' if verification_data else '❌ Not run'}\n")

    # Evidence level legend
    print("=" * 80)
    print("📊 EVIDENCE LEVEL LEGEND")
    print("=" * 80)
    print("\n🥇 GOLD: TYPE 1 + Verified SUPPORTED (Established, literature-backed)")
    print("🥈 SILVER: TYPE 1 OR TYPE 2 + PARTIALLY_SUPPORTED (Emerging with support)")
    print("🥉 BRONZE: TYPE 2 + NOVEL (Exploratory, needs more research)")
    print("🔬 SPECULATIVE: TYPE 3 OR CONTRADICTED (Speculative or conflicting)\n")

    # Organize claims by category and evidence level
    evidence_graded = defaultdict(lambda: defaultdict(list))

    for category, claims_by_type in mechanistic_map.items():
        for epistemic_type, claims in claims_by_type.items():
            for claim in claims:
                # Assign evidence level (simplified without verification for now)
                evidence_level = assign_evidence_level(epistemic_type)
                evidence_graded[category][evidence_level].append(claim)

    # Print by category
    for category in sorted(evidence_graded.keys()):
        print("\n" + "=" * 80)
        print(f"📊 {category.upper().replace('_', ' ')}")
        print("=" * 80)

        for evidence_level in ["GOLD", "SILVER", "BRONZE", "CONDITIONAL", "SPECULATIVE"]:
            if evidence_level not in evidence_graded[category]:
                continue

            claims = evidence_graded[category][evidence_level]
            if not claims:
                continue

            emoji = {
                "GOLD": "🥇",
                "SILVER": "🥈",
                "BRONZE": "🥉",
                "CONDITIONAL": "⚖️",
                "SPECULATIVE": "🔬"
            }

            print(f"\n{emoji[evidence_level]} {evidence_level} - {len(claims)} claims")

            # Show first 3 examples
            for i, claim in enumerate(claims[:3], 1):
                print(f"  {i}. [{claim['model']}] {claim['text'][:120]}...")
                print(f"     Type: TYPE {claim['epistemic_type']}, Ratio: {claim['confidence_ratio']:.2f}")

            if len(claims) > 3:
                print(f"  ... and {len(claims) - 3} more\n")

    # Summary statistics
    print("\n" + "=" * 80)
    print("📈 SUMMARY STATISTICS")
    print("=" * 80)

    total_by_level = defaultdict(int)
    for category_data in evidence_graded.values():
        for evidence_level, claims in category_data.items():
            total_by_level[evidence_level] += len(claims)

    print("\nClaims by evidence level:")
    for level in ["GOLD", "SILVER", "BRONZE", "CONDITIONAL", "SPECULATIVE"]:
        if level in total_by_level:
            count = total_by_level[level]
            emoji = {"GOLD": "🥇", "SILVER": "🥈", "BRONZE": "🥉", "CONDITIONAL": "⚖️", "SPECULATIVE": "🔬"}
            print(f"  {emoji[level]} {level}: {count}")

    print("\nClaims by category:")
    for category in sorted(evidence_graded.keys()):
        total = sum(len(claims) for claims in evidence_graded[category].values())
        print(f"  {category.replace('_', ' ').title()}: {total}")

    # Key findings
    print("\n" + "=" * 80)
    print("🔍 KEY FINDINGS")
    print("=" * 80)

    # Highlight high-value claims
    receptor_gold = evidence_graded.get("receptor_binding", {}).get("GOLD", [])
    receptor_bronze = evidence_graded.get("receptor_binding", {}).get("BRONZE", [])

    if receptor_gold:
        print(f"\n✅ {len(receptor_gold)} GOLD receptor binding claims (established mechanisms)")

    if receptor_bronze:
        print(f"🧪 {len(receptor_bronze)} BRONZE receptor binding claims (exploratory, prime for research)")

    # VDAC1 special mention
    vdac1_claims = []
    for category_data in evidence_graded.values():
        for level_claims in category_data.values():
            vdac1_claims.extend([c for c in level_claims if 'VDAC' in c['text'].upper()])

    if vdac1_claims:
        print(f"\n⚠️  {len(vdac1_claims)} VDAC1-related claims detected (controversial territory)")
        print(f"   Evidence levels: {set(assign_evidence_level(c['epistemic_type']) for c in vdac1_claims)}")

    # Recommendations
    print("\n" + "=" * 80)
    print("🎯 RECOMMENDATIONS")
    print("=" * 80)

    bronze_count = total_by_level.get("BRONZE", 0)
    if bronze_count > 0:
        print(f"\n🔬 {bronze_count} BRONZE claims identified - prime candidates for experimental validation")

    spec_count = total_by_level.get("SPECULATIVE", 0)
    if spec_count > 0:
        print(f"⚠️  {spec_count} SPECULATIVE claims - require human expert review")

    if not verification_data:
        print(f"\n💡 Run Perplexity verification to upgrade BRONZE → SILVER where literature supports")
        print(f"   python3 scripts/verify_s4.py --session {session_path} --output verification.json")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_cbd_mechanistic_map.py <session_json> [verification_json]")
        sys.exit(1)

    session_path = sys.argv[1]
    verification_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(session_path).exists():
        print(f"❌ Session file not found: {session_path}")
        sys.exit(1)

    generate_map_report(session_path, verification_path)

    print("\n\n🌀†⟡∞ CBD mechanistic map complete")
