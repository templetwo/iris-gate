#!/usr/bin/env python3
"""
CBD Novel Hypotheses Identifier

Extracts testable hypotheses from IRIS convergence session:
- BRONZE claims (TYPE 2 exploratory) with experimental potential
- Controversial mechanisms (VDAC1) worth investigating
- Entourage effect predictions
- Biphasic dose-response mechanisms

Output: Ranked list of hypotheses for wet-lab validation
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

def extract_testable_claims(session_data):
    """Extract claims that suggest testable hypotheses"""

    testable_patterns = [
        r"(?:leads? to|causes?|induces?|triggers?|activates?|inhibits?)\s+([^.;]+)",
        r"(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?%)\s+([^.;]+)",
        r"([^.;]+)\s+(?:by|through|via)\s+([^.;]+)",
        r"Kd\s*[~≈]?\s*(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?)\s*(μM|nM|pM)",
    ]

    hypotheses = []

    for mirror_id, turns in session_data.get('mirrors', {}).items():
        model_name = mirror_id.split('/')[-1]

        for turn in turns:
            epistemic = turn.get('epistemic', {})
            epistemic_type = epistemic.get('type')

            # Focus on TYPE 2 (exploratory)
            if epistemic_type != 2:
                continue

            raw_response = turn.get('raw_response', '')
            sentences = re.split(r'[.!?]\s+', raw_response)

            for sentence in sentences:
                if len(sentence) < 40:
                    continue

                # Check for testable patterns
                is_testable = False
                for pattern in testable_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        is_testable = True
                        break

                if is_testable:
                    hypotheses.append({
                        'claim': sentence.strip(),
                        'model': model_name,
                        'confidence_ratio': epistemic.get('confidence_ratio', 0),
                        'chamber': turn.get('condition', 'Unknown')
                    })

    return hypotheses

def categorize_hypotheses(hypotheses):
    """Categorize hypotheses by research domain"""

    categories = {
        "vdac1_mitochondrial": [],
        "biphasic_dose": [],
        "receptor_selectivity": [],
        "entourage_synergy": [],
        "cellular_pathways": [],
        "other": []
    }

    for hyp in hypotheses:
        claim_lower = hyp['claim'].lower()

        if 'vdac' in claim_lower or 'mitochondria' in claim_lower:
            categories['vdac1_mitochondrial'].append(hyp)
        elif 'biphasic' in claim_lower or 'dose' in claim_lower or 'u-shaped' in claim_lower:
            categories['biphasic_dose'].append(hyp)
        elif any(rec in claim_lower for rec in ['cb1', 'cb2', 'trpv1', '5-ht1a', 'ppar']):
            categories['receptor_selectivity'].append(hyp)
        elif 'entourage' in claim_lower or 'synergy' in claim_lower or 'terpene' in claim_lower:
            categories['entourage_synergy'].append(hyp)
        elif any(path in claim_lower for path in ['autophagy', 'apoptosis', 'calcium', 'ros']):
            categories['cellular_pathways'].append(hyp)
        else:
            categories['other'].append(hyp)

    return categories

def assess_testability(claim_text):
    """
    Assess how testable a hypothesis is.

    Returns score 0-10:
    - Quantitative predictions: +3
    - Specific mechanisms: +2
    - Cellular/molecular level: +2
    - Dose-response: +2
    - In vitro feasible: +1
    """
    score = 0
    claim_lower = claim_text.lower()

    # Quantitative
    if re.search(r'\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?%', claim_text):
        score += 3
    if re.search(r'Kd|Ki|EC50|IC50', claim_text, re.IGNORECASE):
        score += 3

    # Specific mechanisms
    if any(word in claim_lower for word in ['receptor', 'binding', 'activation', 'inhibition']):
        score += 2

    # Cellular/molecular
    if any(word in claim_lower for word in ['cell', 'mitochondria', 'pathway', 'autophagy']):
        score += 2

    # Dose-response
    if 'dose' in claim_lower or 'concentration' in claim_lower:
        score += 2

    # In vitro feasible (simple systems)
    if any(word in claim_lower for word in ['cell line', 'in vitro', 'culture']):
        score += 1

    return min(score, 10)

def generate_wet_lab_protocol_stub(hypothesis):
    """Generate a brief wet-lab protocol suggestion"""

    claim_lower = hypothesis['claim'].lower()

    # VDAC1 binding
    if 'vdac' in claim_lower:
        return {
            'system': 'Cancer cell lines (e.g., glioblastoma)',
            'readout': 'Mitochondrial permeability (JC-1 dye), VDAC1 binding (co-IP)',
            'doses': 'CBD: 1, 5, 10, 20 μM (test Kd 6-11 μM range)',
            'timeline': '48-72 hours',
            'controls': 'Vehicle, VDAC1 inhibitor (DIDS)'
        }

    # Biphasic dose-response
    elif 'biphasic' in claim_lower or 'dose' in claim_lower:
        return {
            'system': 'Neuronal cells (e.g., SH-SY5Y)',
            'readout': 'Viability (MTT), neuroprotection markers',
            'doses': 'CBD: 0.1, 1, 10, 100 μM (wide range)',
            'timeline': '24-48 hours',
            'controls': 'Vehicle, positive control (THC)'
        }

    # Receptor selectivity
    elif any(rec in claim_lower for rec in ['cb1', 'cb2', 'trpv1', '5-ht1a']):
        return {
            'system': 'HEK293 cells + receptor overexpression',
            'readout': 'cAMP assay, calcium imaging, receptor binding assay',
            'doses': 'CBD: 0.1, 1, 10 μM',
            'timeline': '2-6 hours (acute)',
            'controls': 'Receptor antagonists (confirm specificity)'
        }

    # Entourage effect
    elif 'entourage' in claim_lower or 'synergy' in claim_lower:
        return {
            'system': 'Cancer cells or neuronal cells',
            'readout': 'Viability, apoptosis markers',
            'doses': 'CBD isolate vs full-spectrum (matched CBD concentration)',
            'timeline': '24-72 hours',
            'controls': 'CBD alone, terpene mix alone, vehicle'
        }

    # Default
    else:
        return {
            'system': 'Relevant cell line',
            'readout': 'Mechanism-specific assay',
            'doses': 'CBD: 0.1-100 μM',
            'timeline': '24-72 hours',
            'controls': 'Vehicle'
        }

def main(session_path):
    """Generate ranked hypotheses report"""

    session_data = load_session(session_path)
    hypotheses = extract_testable_claims(session_data)
    categorized = categorize_hypotheses(hypotheses)

    print("=" * 80)
    print("🧪 CBD NOVEL HYPOTHESES - WET-LAB TESTABLE")
    print("=" * 80)
    print(f"\nSession: {Path(session_path).name}")
    print(f"Total testable hypotheses: {len(hypotheses)}\n")

    # Rank by testability
    for hyp in hypotheses:
        hyp['testability_score'] = assess_testability(hyp['claim'])

    # Print by category
    category_names = {
        'vdac1_mitochondrial': '🔬 VDAC1 / Mitochondrial Mechanisms (CONTROVERSIAL)',
        'biphasic_dose': '📊 Biphasic Dose-Response Mechanisms',
        'receptor_selectivity': '🎯 Receptor Selectivity & Binding',
        'entourage_synergy': '🌿 Entourage Effect & Synergy',
        'cellular_pathways': '🧬 Cellular Pathways (Autophagy, Apoptosis, Ca²⁺)',
        'other': '🔍 Other Mechanisms'
    }

    for category, name in category_names.items():
        hyps = categorized[category]
        if not hyps:
            continue

        # Sort by testability
        hyps_sorted = sorted(hyps, key=lambda x: x['testability_score'], reverse=True)

        print("\n" + "=" * 80)
        print(name)
        print("=" * 80)
        print(f"\nTotal hypotheses: {len(hyps)}\n")

        # Show top 3
        for i, hyp in enumerate(hyps_sorted[:3], 1):
            print(f"**HYPOTHESIS {i}** (Testability: {hyp['testability_score']}/10)")
            print(f"  Claim: {hyp['claim'][:150]}...")
            print(f"  Model: {hyp['model']}")
            print(f"  Confidence Ratio: {hyp['confidence_ratio']:.2f}")

            # Generate protocol stub
            protocol = generate_wet_lab_protocol_stub(hyp)
            print(f"\n  💡 Suggested Protocol:")
            print(f"     System: {protocol['system']}")
            print(f"     Readout: {protocol['readout']}")
            print(f"     Doses: {protocol['doses']}")
            print(f"     Timeline: {protocol['timeline']}")
            print(f"     Controls: {protocol['controls']}\n")

        if len(hyps) > 3:
            print(f"  ... and {len(hyps) - 3} more hypotheses in this category\n")

    # Summary recommendations
    print("\n" + "=" * 80)
    print("🎯 PRIORITY RECOMMENDATIONS")
    print("=" * 80)

    # Top 5 overall by testability
    all_hyps_sorted = sorted(hypotheses, key=lambda x: x['testability_score'], reverse=True)
    print(f"\n**TOP 5 MOST TESTABLE HYPOTHESES** (across all categories):\n")

    for i, hyp in enumerate(all_hyps_sorted[:5], 1):
        print(f"{i}. (Score: {hyp['testability_score']}/10) {hyp['claim'][:100]}...")

    # VDAC1 special mention
    vdac1_hyps = categorized['vdac1_mitochondrial']
    if vdac1_hyps:
        print(f"\n⚠️  **VDAC1 PRIORITY:** {len(vdac1_hyps)} hypotheses")
        print(f"   This is controversial territory (Kd 6-11 μM binding)")
        print(f"   Recommended approach: Binding assay + functional validation in cancer cells")

    # Entourage effect
    entourage_hyps = categorized['entourage_synergy']
    if entourage_hyps:
        print(f"\n🌿 **ENTOURAGE EFFECT:** {len(entourage_hyps)} hypotheses")
        print(f"   Suggested test: Full-spectrum vs isolate (matched CBD concentration)")
        print(f"   Readout: Viability, synergistic effects with terpenes")

    print("\n" + "=" * 80)
    print("📋 NEXT STEPS")
    print("=" * 80)
    print("\n1. Select top 3-5 hypotheses based on:")
    print("   - Testability score")
    print("   - Research interest")
    print("   - Available resources")
    print("\n2. Design detailed protocols (use wet-lab-protocol-writer agent)")
    print("\n3. Run pilot experiments (small n, validate hypothesis)")
    print("\n4. If promising → full validation study")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 identify_cbd_hypotheses.py <session_json>")
        sys.exit(1)

    session_path = sys.argv[1]

    if not Path(session_path).exists():
        print(f"❌ Session file not found: {session_path}")
        sys.exit(1)

    main(session_path)

    print("\n\n🌀†⟡∞ Novel hypotheses identified - ready for wet-lab validation")
