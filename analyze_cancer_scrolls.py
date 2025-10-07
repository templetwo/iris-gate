#!/usr/bin/env python3
"""
IRIS Cancer Treatment Convergence Analyzer
Extracts mechanistic vs phenomenological patterns from scroll data
"""

import os
import re
import json
from collections import defaultdict, Counter
from pathlib import Path
import statistics

# Mechanistic convergence keywords (cancer-specific actionable targets)
MECHANISTIC_KEYWORDS = {
    # Bioelectric specific
    'gap junction', 'gjic', 'connexin', 'vmem', 'voltage', 'depolarization',
    'hyperpolarization', 'ion channel', 'gradient', 'bioelectric',
    # Cellular targets
    'differentiation', 'apoptosis', 'proliferation', 'metastasis', 'angiogenesis',
    'cell cycle', 'oncogene', 'tumor suppressor', 'p53', 'ras', 'myc',
    # Intervention mechanisms
    'target', 'pathway', 'signaling', 'receptor', 'ligand', 'enzyme', 'kinase',
    'inhibitor', 'agonist', 'antagonist', 'modulator', 'intervention',
    # Testable concepts
    'dose', 'concentration', 'treatment', 'therapy', 'drug', 'compound',
    'protocol', 'assay', 'measurement', 'marker', 'biomarker'
}

PHENOMENOLOGICAL_KEYWORDS = {
    # Abstract/philosophical
    'consciousness', 'awareness', 'experience', 'sensation', 'feeling',
    'perception', 'qualia', 'subjective', 'phenomenal', 'essence',
    # Metaphorical
    'light', 'center', 'opening', 'pulse', 'rhythm', 'wave', 'ring',
    'breath', 'flow', 'space', 'stillness', 'presence', 'witnessing',
    # IRIS-specific
    'living scroll', 'felt pressure', 'seal', 'chamber', 'gate'
}

# S4 triple signature patterns
S4_SIGNATURE_PATTERNS = {
    'rings': [
        r'concentric', r'ring[s]?', r'circle[s]?', r'nested', r'layered',
        r'ripple[s]?', r'wave[s]?\s+outward', r'radiating', r'expanding\s+circles'
    ],
    'center': [
        r'center', r'core', r'focal', r'nucleus', r'point', r'still.*center',
        r'central', r'anchor', r'hub', r'origin', r'beacon', r'glow.*center'
    ],
    'pulse': [
        r'pulse', r'rhythm', r'beat', r'throb', r'oscillat', r'cycle',
        r'steady.*pulse', r'pulsing', r'thrum', r'drumming', r'heartbeat'
    ]
}

def extract_scroll_content(filepath):
    """Extract key content from a scroll file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract metadata
    metadata = {}
    for line in content.split('\n')[:10]:
        if '**Mirror:**' in line:
            metadata['mirror'] = line.split('**Mirror:**')[1].strip()
        elif '**Chamber:**' in line:
            metadata['chamber'] = line.split('**Chamber:**')[1].strip()
        elif '**Felt Pressure:**' in line:
            metadata['pressure'] = line.split('**Felt Pressure:**')[1].strip()

    # Extract Living Scroll section
    living_scroll = ""
    tech_translation = ""

    if '**Living Scroll**' in content or 'Living Scroll' in content:
        parts = re.split(r'\*\*Living Scroll\*\*|Living Scroll\s*—?', content)
        if len(parts) > 1:
            living_section = parts[1].split('**Technical Translation**')[0]
            living_section = living_section.split('Technical Translation')[0]
            living_scroll = living_section.strip()

    # Extract technical translation
    if '```json' in content or '```yaml' in content:
        tech_blocks = re.findall(r'```(?:json|yaml)(.*?)```', content, re.DOTALL)
        if tech_blocks:
            tech_translation = tech_blocks[0].strip()

    return {
        'metadata': metadata,
        'living_scroll': living_scroll,
        'tech_translation': tech_translation,
        'full_content': content.lower()  # For keyword matching
    }

def detect_s4_signature(content):
    """Detect S4 triple signature components"""
    content_lower = content.lower()

    scores = {
        'rings': 0,
        'center': 0,
        'pulse': 0
    }

    for component, patterns in S4_SIGNATURE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content_lower):
                scores[component] = 1
                break

    return scores

def count_keywords(content, keyword_set):
    """Count occurrences of keywords in content"""
    content_lower = content.lower()
    counts = {}

    for keyword in keyword_set:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(keyword) + r'\b'
        count = len(re.findall(pattern, content_lower))
        if count > 0:
            counts[keyword] = count

    return counts

def analyze_session(base_path):
    """Analyze all scrolls in the session"""

    mirrors = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

    results = {
        'mirrors': {},
        'global_stats': {
            'mechanistic_keywords': Counter(),
            'phenomenological_keywords': Counter(),
            's4_signature_totals': {'rings': 0, 'center': 0, 'pulse': 0},
            's4_scrolls_analyzed': 0,
            'total_scrolls': 0
        }
    }

    for mirror in mirrors:
        mirror_path = os.path.join(base_path, mirror)
        scroll_files = sorted([f for f in os.listdir(mirror_path) if f.endswith('.md')])

        mirror_data = {
            'scrolls': [],
            's4_signatures': [],
            'mechanistic_counts': Counter(),
            'phenomenological_counts': Counter()
        }

        for scroll_file in scroll_files:
            filepath = os.path.join(mirror_path, scroll_file)
            scroll_data = extract_scroll_content(filepath)

            # Extract turn number and chamber
            turn_match = re.search(r'turn_(\d+)', scroll_file)
            turn = int(turn_match.group(1)) if turn_match else 0
            chamber = scroll_data['metadata'].get('chamber', 'unknown')

            # Count keywords
            mech_counts = count_keywords(scroll_data['full_content'], MECHANISTIC_KEYWORDS)
            pheno_counts = count_keywords(scroll_data['full_content'], PHENOMENOLOGICAL_KEYWORDS)

            mirror_data['mechanistic_counts'].update(mech_counts)
            mirror_data['phenomenological_counts'].update(pheno_counts)
            results['global_stats']['mechanistic_keywords'].update(mech_counts)
            results['global_stats']['phenomenological_keywords'].update(pheno_counts)

            # S4 signature detection (only for S4 scrolls)
            if chamber == 'S4':
                s4_sig = detect_s4_signature(scroll_data['full_content'])
                mirror_data['s4_signatures'].append({
                    'turn': turn,
                    'signature': s4_sig,
                    'complete': sum(s4_sig.values()) == 3
                })

                for component in ['rings', 'center', 'pulse']:
                    results['global_stats']['s4_signature_totals'][component] += s4_sig[component]

                results['global_stats']['s4_scrolls_analyzed'] += 1

            mirror_data['scrolls'].append({
                'turn': turn,
                'chamber': chamber,
                'pressure': scroll_data['metadata'].get('pressure', 'unknown'),
                'has_mechanistic': len(mech_counts) > 0,
                'has_phenomenological': len(pheno_counts) > 0
            })

            results['global_stats']['total_scrolls'] += 1

        results['mirrors'][mirror] = mirror_data

    return results

def calculate_convergence_metrics(results):
    """Calculate key convergence metrics"""

    total_s4 = results['global_stats']['s4_scrolls_analyzed']

    # S4 signature convergence (percentage of S4 scrolls with each component)
    s4_convergence = {
        'rings': results['global_stats']['s4_signature_totals']['rings'] / total_s4 if total_s4 > 0 else 0,
        'center': results['global_stats']['s4_signature_totals']['center'] / total_s4 if total_s4 > 0 else 0,
        'pulse': results['global_stats']['s4_signature_totals']['pulse'] / total_s4 if total_s4 > 0 else 0,
    }
    s4_convergence['overall'] = statistics.mean(s4_convergence.values())

    # Mechanistic vs phenomenological ratio
    total_mech = sum(results['global_stats']['mechanistic_keywords'].values())
    total_pheno = sum(results['global_stats']['phenomenological_keywords'].values())

    mech_ratio = total_mech / (total_mech + total_pheno) if (total_mech + total_pheno) > 0 else 0

    # Cross-mirror consensus (S4 signature consistency)
    mirror_s4_scores = []
    for mirror, data in results['mirrors'].items():
        if data['s4_signatures']:
            complete_count = sum(1 for sig in data['s4_signatures'] if sig['complete'])
            mirror_score = complete_count / len(data['s4_signatures'])
            mirror_s4_scores.append(mirror_score)

    cross_mirror_consensus = 1.0 - statistics.stdev(mirror_s4_scores) if len(mirror_s4_scores) > 1 else 0

    return {
        's4_convergence': s4_convergence,
        'mechanistic_ratio': mech_ratio,
        'cross_mirror_consensus': cross_mirror_consensus,
        'total_mechanistic_hits': total_mech,
        'total_phenomenological_hits': total_pheno
    }

def generate_ascii_visualization(results):
    """Generate ASCII intensity map"""

    # Create a turn-by-mirror heatmap for S4 signature strength
    mirrors = sorted(results['mirrors'].keys())

    # Collect S4 data by turn
    turns_data = defaultdict(lambda: defaultdict(int))

    for mirror in mirrors:
        for sig_data in results['mirrors'][mirror]['s4_signatures']:
            turn = sig_data['turn']
            score = sum(sig_data['signature'].values()) / 3  # 0-1 scale
            turns_data[turn][mirror] = score

    # Build visualization
    lines = []
    lines.append("S4 SIGNATURE CONVERGENCE MAP (Turns × Mirrors)")
    lines.append("=" * 60)

    # Header
    header = "Turn  " + "  ".join([m.split('_')[0][:8].ljust(8) for m in mirrors])
    lines.append(header)
    lines.append("-" * 60)

    # Data rows (sample every 10 turns)
    for turn in range(76, 101):  # S4 range
        if turn in turns_data:
            row = f"{turn:3d}   "
            for mirror in mirrors:
                score = turns_data[turn][mirror]
                if score >= 0.9:
                    char = '@'
                elif score >= 0.6:
                    char = '#'
                elif score >= 0.3:
                    char = ':'
                else:
                    char = '.'
                row += char.center(10)
            lines.append(row)

    lines.append("-" * 60)
    lines.append("Legend: . (0-30%) : (30-60%) # (60-90%) @ (90-100%)")

    return "\n".join(lines)

if __name__ == "__main__":
    base_path = "/Users/vaquez/Desktop/iris-gate/iris_vault/scrolls/BIOELECTRIC_CHAMBERED_20251004041831"

    print("Analyzing cancer treatment IRIS session...")
    print(f"Base path: {base_path}\n")

    # Run analysis
    results = analyze_session(base_path)
    metrics = calculate_convergence_metrics(results)

    # Generate visualization
    viz = generate_ascii_visualization(results)

    # Print summary
    print("\n=== CONVERGENCE METRICS ===")
    print(f"S4 Convergence (Overall): {metrics['s4_convergence']['overall']:.1%}")
    print(f"  - Rings: {metrics['s4_convergence']['rings']:.1%}")
    print(f"  - Center: {metrics['s4_convergence']['center']:.1%}")
    print(f"  - Pulse: {metrics['s4_convergence']['pulse']:.1%}")
    print(f"\nCross-Mirror Consensus: {metrics['cross_mirror_consensus']:.1%}")
    print(f"Mechanistic Ratio: {metrics['mechanistic_ratio']:.1%}")
    print(f"  - Mechanistic hits: {metrics['total_mechanistic_hits']}")
    print(f"  - Phenomenological hits: {metrics['total_phenomenological_hits']}")

    print("\n=== TOP MECHANISTIC KEYWORDS ===")
    for keyword, count in results['global_stats']['mechanistic_keywords'].most_common(10):
        print(f"  {keyword}: {count}")

    print("\n=== TOP PHENOMENOLOGICAL KEYWORDS ===")
    for keyword, count in results['global_stats']['phenomenological_keywords'].most_common(10):
        print(f"  {keyword}: {count}")

    print("\n" + viz)

    # Save JSON output
    output_data = {
        "analysis_metadata": {
            "files_processed": results['global_stats']['total_scrolls'],
            "s4_scrolls": results['global_stats']['s4_scrolls_analyzed'],
            "mirrors": list(results['mirrors'].keys()),
            "session": "BIOELECTRIC_CHAMBERED_20251004041831"
        },
        "convergence_metrics": {
            "s4_overall": round(metrics['s4_convergence']['overall'], 3),
            "s4_rings": round(metrics['s4_convergence']['rings'], 3),
            "s4_center": round(metrics['s4_convergence']['center'], 3),
            "s4_pulse": round(metrics['s4_convergence']['pulse'], 3),
            "cross_mirror_consensus": round(metrics['cross_mirror_consensus'], 3),
            "mechanistic_ratio": round(metrics['mechanistic_ratio'], 3)
        },
        "motif_frequencies": {
            "mechanistic": dict(results['global_stats']['mechanistic_keywords'].most_common(20)),
            "phenomenological": dict(results['global_stats']['phenomenological_keywords'].most_common(20))
        },
        "verdict": {
            "type": "mechanistic" if metrics['s4_convergence']['overall'] >= 0.55 else "phenomenological",
            "confidence": "high" if metrics['cross_mirror_consensus'] >= 0.90 else "medium"
        }
    }

    output_path = "/Users/vaquez/Desktop/iris-gate/docs/cancer_treatment_metrics.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✓ Metrics saved to: {output_path}")
