#!/usr/bin/env python3
"""
Epistemic Scan - Classify IRIS Gate scrolls by topology type

Usage:
    python3 epistemic_scan.py <scroll_file>
    python3 epistemic_scan.py iris_vault/scrolls/IRIS_*/S4.md
    python3 epistemic_scan.py --session iris_vault/session_*.json

Examples:
    # Scan single scroll
    python3 epistemic_scan.py iris_vault/scrolls/IRIS_20251015/S4.md

    # Scan all S4 scrolls in a session
    python3 epistemic_scan.py iris_vault/scrolls/IRIS_*/S4.md

    # Analyze full session JSON
    python3 epistemic_scan.py --session iris_vault/session_20251015_052400.json
"""

import sys
import json
import argparse
from pathlib import Path
from modules.epistemic_map import classify_response, format_classification_table


def scan_scroll_file(scroll_path: Path) -> dict:
    """
    Scan a single scroll markdown file.

    Args:
        scroll_path: Path to scroll .md file

    Returns:
        Classification dict
    """
    if not scroll_path.exists():
        print(f"✗ File not found: {scroll_path}")
        return None

    content = scroll_path.read_text()

    # Extract raw response (between first --- and second ---, or epistemic footer)
    parts = content.split('---')
    if len(parts) >= 3:
        raw_response = parts[1].strip()
    else:
        raw_response = content

    return classify_response(raw_response)


def scan_session_json(session_path: Path) -> dict:
    """
    Scan full session JSON with epistemic drift analysis.

    Args:
        session_path: Path to session JSON file

    Returns:
        Dict with scan results and drift analysis
    """
    if not session_path.exists():
        print(f"✗ File not found: {session_path}")
        return None

    session_data = json.loads(session_path.read_text())

    results = {
        'session_file': str(session_path),
        'mirrors': {},
        'summary': {
            'total_turns': 0,
            'type_distribution': {},
            'drift_detected': False
        }
    }

    all_types = []

    for mirror_id, turns in session_data.get('mirrors', {}).items():
        mirror_results = []

        for turn in turns:
            if 'epistemic' in turn:
                ep = turn['epistemic']
                mirror_results.append(ep)
                all_types.append(ep['type'])
            elif 'raw_response' in turn:
                # Classify on-the-fly if not already classified
                classification = classify_response(turn['raw_response'])
                mirror_results.append(classification)
                all_types.append(classification['type'])

        results['mirrors'][mirror_id] = mirror_results

    # Compute summary stats
    from collections import Counter
    type_counts = Counter(all_types)
    results['summary'] = {
        'total_turns': len(all_types),
        'type_distribution': dict(type_counts),
        'drift_detected': len(set(all_types)) > 1,
        'dominant_type': type_counts.most_common(1)[0][0] if all_types else None
    }

    return results


def print_session_summary(results: dict):
    """Print readable summary of session scan."""
    print("\n" + "="*60)
    print("EPISTEMIC SESSION SCAN")
    print("="*60)
    print(f"\nSession: {results['session_file']}")
    print(f"Total Turns: {results['summary']['total_turns']}")
    print(f"Drift Detected: {'YES' if results['summary']['drift_detected'] else 'NO'}")

    if results['summary']['dominant_type'] is not None:
        print(f"Dominant Type: {results['summary']['dominant_type']}")

    print("\n📊 Type Distribution:")
    for type_id, count in sorted(results['summary']['type_distribution'].items()):
        pct = (count / results['summary']['total_turns']) * 100
        print(f"  TYPE {type_id}: {count} turns ({pct:.1f}%)")

    print("\n🔍 By Mirror:")
    for mirror_id, classifications in results['mirrors'].items():
        types = [c['type'] for c in classifications]
        ratios = [c.get('ratio', c.get('confidence_ratio', 0)) for c in classifications]
        mean_ratio = sum(ratios) / len(ratios) if ratios else 0

        if len(set(types)) == 1:
            stability = f"Stable TYPE {types[0]}"
        else:
            stability = f"Drift: {' → '.join(map(str, types))}"

        print(f"\n  {mirror_id}")
        print(f"    Pattern: {stability}")
        print(f"    Mean Ratio: {mean_ratio:.2f}")


def main():
    parser = argparse.ArgumentParser(
        description="Epistemic Scan - Classify IRIS Gate scrolls by topology type",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('scroll_path', nargs='?', help='Path to scroll file or glob pattern')
    parser.add_argument('--session', help='Path to session JSON file')
    parser.add_argument('--cbd', action='store_true', help='Test with CBD paradox examples')

    args = parser.parse_args()

    if args.cbd:
        # Run CBD test examples
        from modules.epistemic_map import test_cbd_snippet
        test_cbd_snippet()
        return

    if args.session:
        # Scan session JSON
        results = scan_session_json(Path(args.session))
        if results:
            print_session_summary(results)
        return

    if not args.scroll_path:
        parser.print_help()
        return

    # Scan individual scroll(s)
    scroll_paths = list(Path().glob(args.scroll_path))

    if not scroll_paths:
        # Try as exact path
        scroll_paths = [Path(args.scroll_path)]

    for scroll_path in scroll_paths:
        if not scroll_path.exists():
            print(f"\n✗ Not found: {scroll_path}")
            continue

        print(f"\n📄 {scroll_path}")
        print("-" * 60)

        result = scan_scroll_file(scroll_path)
        if result:
            print(format_classification_table(result))


if __name__ == "__main__":
    main()
