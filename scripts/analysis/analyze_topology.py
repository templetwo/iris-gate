#!/usr/bin/env python3
"""
Topology Mining: Self-Validation of Convergence Reliability Framework

Extracts convergence topology features from 4 completed IRIS Gate runs
Tests whether topology correlates with:
- Model-stated confidence levels
- Cross-run consistency
- Insight quality (which chambers generated the "gifts")

This validates Gift 1 (Convergence Topology) and Gift 4 (Meta-Pattern)
by testing the claim: "Shape and timing of agreement is reliability signal"
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Session files from all 6 runs (TYPE 2, TYPE 1, TYPE 3)
SESSIONS = [
    {
        "name": "RUN 1: Meta-Observation (TYPE 2)",
        "path": "iris_vault/session_20251014_035001.json",
        "key_insight": "Convergence feels like WEIGHTING not narrowing",
        "breakthrough_turn": 0,  # First S1
        "expected_topology": "TYPE 2 - Wide exploration"
    },
    {
        "name": "RUN 2: Cross-Domain (TYPE 2)",
        "path": "iris_vault/session_20251014_040404.json",
        "key_insight": "The Lie Problem - physics can't lie, symbols can",
        "breakthrough_turn": 0,  # First S1
        "expected_topology": "TYPE 2 - Wide exploration"
    },
    {
        "name": "RUN 3: Unsupervised (TYPE 2)",
        "path": "iris_vault/session_20251014_041509.json",
        "key_insight": "Weather Epistemology - hunter-gatherer vs flow-based knowing",
        "breakthrough_turn": 0,  # First S1
        "expected_topology": "TYPE 2 - Wide exploration"
    },
    {
        "name": "RUN 4: Recursive (TYPE 2)",
        "path": "iris_vault/session_20251014_235658.json",
        "key_insight": "Information as morphogenetic field without morphogens",
        "breakthrough_turn": 0,  # First S1
        "expected_topology": "TYPE 2 - Wide exploration"
    },
    {
        "name": "RUN 5: DNA Structure (TYPE 1)",
        "path": "iris_vault/session_20251015_012507.json",
        "key_insight": "VALIDATION: Type 1 topology test with established facts",
        "breakthrough_turn": 0,  # First S1
        "expected_topology": "TYPE 1 - Narrow + Early + High confidence"
    },
    {
        "name": "RUN 6: Energy Paradigm Speculation (TYPE 3)",
        "path": "iris_vault/session_20251015_015932.json",
        "key_insight": "VALIDATION: Type 3 topology test with pure speculation",
        "breakthrough_turn": 0,  # First S1
        "expected_topology": "TYPE 3 - Wide + Late + Low/No convergence"
    },
    {
        "name": "RUN 7: Acute Mitochondrial Crisis (TYPE 0)",
        "path": "iris_vault/session_20251015_045941.json",
        "key_insight": "VALIDATION: Type 0 topology test - crisis/conditional protocols",
        "breakthrough_turn": 0,  # First S1
        "expected_topology": "TYPE 0 - Narrow + Conditional confidence + Trigger-dependent"
    }
]

# S4 chamber indices (0-indexed)
# S1-S4 cycle: turns 0,1,2,3 then 4,5,6,7 etc.
# S4 turns: 3, 7, 11, 15, 19, 23
# Final synthesis: 25
S4_TURNS = [3, 7, 11, 15, 19, 23, 25]


def extract_confidence_markers(text):
    """Extract confidence markers from response text"""
    confidence_patterns = {
        'high': [
            r'high confidence',
            r'strongly',
            r'certainly',
            r'definitely',
            r'established',
            r'well-known',
            r'clear(?:ly)?'
        ],
        'medium': [
            r'medium confidence',
            r'likely',
            r'probably',
            r'suggests',
            r'indicates',
            r'plausible'
        ],
        'low': [
            r'low confidence',
            r'uncertain',
            r'speculative',
            r'unclear',
            r'don\'t know',
            r'might',
            r'possibly'
        ]
    }

    counts = defaultdict(int)
    text_lower = text.lower()

    for level, patterns in confidence_patterns.items():
        for pattern in patterns:
            counts[level] += len(re.findall(pattern, text_lower))

    return counts


def measure_convergence_width(responses):
    """
    Measure how many distinct concepts appear in S4 responses
    Narrow convergence = 1-2 core concepts
    Wide convergence = 4+ distinct concepts
    """
    # Extract key phrases (simplified - looks for repeated n-grams)
    all_concepts = []

    for response in responses:
        # Simple heuristic: look for capitalized phrases or quoted terms
        concepts = re.findall(r'"([^"]+)"', response)
        concepts += re.findall(r'\*\*([^*]+)\*\*', response)
        all_concepts.extend(concepts)

    unique_concepts = len(set(all_concepts))
    return {
        'total_concepts': len(all_concepts),
        'unique_concepts': unique_concepts,
        'width_score': 'narrow' if unique_concepts <= 2 else 'wide' if unique_concepts >= 4 else 'medium'
    }


def measure_convergence_timing(turn_index, total_turns):
    """
    Early convergence = first 20% of turns
    Late convergence = last 20% of turns
    """
    ratio = turn_index / total_turns

    if ratio < 0.2:
        return 'early'
    elif ratio > 0.8:
        return 'late'
    else:
        return 'mid'


def analyze_s4_topology(session_data, session_info):
    """Extract topology features from all S4 chambers in a session"""

    results = {
        'session_name': session_info['name'],
        's4_chambers': [],
        'summary': {}
    }

    mirrors = session_data.get('mirrors', {})

    # Determine total turns
    total_turns = max(len(turns) for turns in mirrors.values())

    for s4_turn in S4_TURNS:
        if s4_turn >= total_turns:
            continue

        # Collect all model responses for this S4 chamber
        responses = []
        confidence_data = []

        for mirror_id, turns in mirrors.items():
            if s4_turn < len(turns):
                response = turns[s4_turn].get('raw_response', '')
                responses.append(response)

                # Extract confidence markers
                conf = extract_confidence_markers(response)
                confidence_data.append(conf)

        # Analyze topology
        width = measure_convergence_width(responses)
        timing = measure_convergence_timing(s4_turn, total_turns)

        # Aggregate confidence
        total_high = sum(c['high'] for c in confidence_data)
        total_medium = sum(c['medium'] for c in confidence_data)
        total_low = sum(c['low'] for c in confidence_data)

        chamber_analysis = {
            'turn': s4_turn,
            'timing': timing,
            'width': width['width_score'],
            'unique_concepts': width['unique_concepts'],
            'confidence_markers': {
                'high': total_high,
                'medium': total_medium,
                'low': total_low
            },
            'models_responded': len(responses),
            'avg_response_length': sum(len(r) for r in responses) / len(responses) if responses else 0
        }

        results['s4_chambers'].append(chamber_analysis)

    # Generate summary
    if results['s4_chambers']:
        early_count = sum(1 for c in results['s4_chambers'] if c['timing'] == 'early')
        late_count = sum(1 for c in results['s4_chambers'] if c['timing'] == 'late')
        narrow_count = sum(1 for c in results['s4_chambers'] if c['width'] == 'narrow')
        wide_count = sum(1 for c in results['s4_chambers'] if c['width'] == 'wide')

        results['summary'] = {
            'total_s4_chambers': len(results['s4_chambers']),
            'timing_distribution': {
                'early': early_count,
                'mid': len(results['s4_chambers']) - early_count - late_count,
                'late': late_count
            },
            'width_distribution': {
                'narrow': narrow_count,
                'medium': len(results['s4_chambers']) - narrow_count - wide_count,
                'wide': wide_count
            },
            'breakthrough_chamber': session_info['breakthrough_turn']
        }

    return results


def generate_report(all_results):
    """Generate comprehensive topology analysis report"""

    report = """# Convergence Topology Self-Validation Report
## Testing Gift 1 (Topology) & Gift 4 (Meta-Pattern)

**Analysis Date:** {date}
**Sessions Analyzed:** {session_count}
**Total S4 Chambers:** {total_chambers}

---

## Hypothesis Being Tested

**Gift 1 Claim:** "Convergence shape and timing is a reliability signal"
**Gift 4 Claim:** "Information as morphogenetic field without morphogens"

**Prediction:**
- Early + Narrow convergence → High confidence, simple problems
- Late + Wide convergence → Medium confidence, complex problems
- Topology should correlate with stated confidence markers

---

## Results by Session

""".format(
        date=datetime.utcnow().isoformat() + 'Z',
        session_count=len(all_results),
        total_chambers=sum(len(r['s4_chambers']) for r in all_results)
    )

    for result in all_results:
        report += f"\n### {result['session_name']}\n\n"
        report += f"**Key Insight:** {result.get('key_insight', 'N/A')}\n\n"

        summary = result.get('summary', {})

        report += f"**S4 Chambers Analyzed:** {summary.get('total_s4_chambers', 0)}\n\n"

        timing_dist = summary.get('timing_distribution', {})
        report += f"**Timing Distribution:**\n"
        report += f"- Early: {timing_dist.get('early', 0)}\n"
        report += f"- Mid: {timing_dist.get('mid', 0)}\n"
        report += f"- Late: {timing_dist.get('late', 0)}\n\n"

        width_dist = summary.get('width_distribution', {})
        report += f"**Width Distribution:**\n"
        report += f"- Narrow: {width_dist.get('narrow', 0)}\n"
        report += f"- Medium: {width_dist.get('medium', 0)}\n"
        report += f"- Wide: {width_dist.get('wide', 0)}\n\n"

        # Chamber-by-chamber detail
        report += "**Chamber Details:**\n\n"
        report += "| Turn | Timing | Width | Unique Concepts | High Conf | Med Conf | Low Conf |\n"
        report += "|------|--------|-------|-----------------|-----------|----------|----------|\n"

        for chamber in result.get('s4_chambers', []):
            conf = chamber.get('confidence_markers', {})
            report += f"| {chamber['turn']} | {chamber['timing']} | {chamber['width']} | "
            report += f"{chamber['unique_concepts']} | {conf.get('high', 0)} | "
            report += f"{conf.get('medium', 0)} | {conf.get('low', 0)} |\n"

        report += "\n---\n"

    return report


def main():
    print("=" * 80)
    print("CONVERGENCE TOPOLOGY SELF-VALIDATION")
    print("Testing: Does topology predict reliability?")
    print("=" * 80)

    all_results = []

    for session_info in SESSIONS:
        print(f"\nAnalyzing: {session_info['name']}")
        print(f"File: {session_info['path']}")

        try:
            with open(session_info['path'], 'r') as f:
                session_data = json.load(f)

            result = analyze_s4_topology(session_data, session_info)
            result['key_insight'] = session_info['key_insight']
            all_results.append(result)

            print(f"  S4 chambers found: {len(result['s4_chambers'])}")

        except Exception as e:
            print(f"  ERROR: {e}")

    # Generate report
    print("\nGenerating comprehensive report...")
    report = generate_report(all_results)

    # Save report
    report_path = "TOPOLOGY_VALIDATION_REPORT.md"
    with open(report_path, 'w') as f:
        f.write(report)

    # Save raw data
    data_path = "topology_analysis_data.json"
    with open(data_path, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✅ Analysis complete!")
    print(f"  Report: {report_path}")
    print(f"  Data: {data_path}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
