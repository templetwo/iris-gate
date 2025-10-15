#!/usr/bin/env python3
"""
Epistemic Drift Logger - Track topology type stability over time

Usage:
    python3 epistemic_drift.py <session_dir>
    python3 epistemic_drift.py iris_vault/
    python3 epistemic_drift.py --compare session1.json session2.json

Examples:
    # Analyze drift in a vault directory
    python3 epistemic_drift.py iris_vault/

    # Compare two sessions (e.g., CBD v1 vs v2)
    python3 epistemic_drift.py --compare \
        iris_vault/session_20251014_010158.json \
        iris_vault/session_20251014_041558.json

    # Track drift across all sessions
    python3 epistemic_drift.py iris_vault/ --all-sessions
"""

import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
from modules.epistemic_map import classify_response


def analyze_session_drift(session_path: Path) -> dict:
    """
    Analyze epistemic drift within a single session.

    Args:
        session_path: Path to session JSON

    Returns:
        Drift analysis dict
    """
    if not session_path.exists():
        return None

    session_data = json.loads(session_path.read_text())

    drift_analysis = {
        'session_file': str(session_path),
        'session_start': session_data.get('session_start', 'Unknown'),
        'mirrors': {},
        'summary': {
            'drift_detected': False,
            'stable_mirrors': 0,
            'drifting_mirrors': 0,
            'dominant_type': None
        }
    }

    all_types = []

    for mirror_id, turns in session_data.get('mirrors', {}).items():
        types = []
        ratios = []

        for turn in turns:
            if 'epistemic' in turn:
                ep = turn['epistemic']
                types.append(ep['type'])
                ratios.append(ep.get('confidence_ratio', ep.get('ratio', 0)))
                all_types.append(ep['type'])

        # Detect drift
        drift_detected = len(set(types)) > 1
        if drift_detected:
            drift_pattern = ' → '.join(map(str, types))
            drift_analysis['summary']['drifting_mirrors'] += 1
        else:
            drift_pattern = f"Stable TYPE {types[0]}" if types else "No data"
            drift_analysis['summary']['stable_mirrors'] += 1

        drift_analysis['mirrors'][mirror_id] = {
            'types': types,
            'ratios': ratios,
            'drift_detected': drift_detected,
            'drift_pattern': drift_pattern,
            'mean_ratio': sum(ratios) / len(ratios) if ratios else 0.0,
            'ratio_range': (min(ratios), max(ratios)) if ratios else (0, 0)
        }

    # Session-wide drift
    drift_analysis['summary']['drift_detected'] = len(set(all_types)) > 1

    if all_types:
        from collections import Counter
        dominant = Counter(all_types).most_common(1)[0][0]
        drift_analysis['summary']['dominant_type'] = dominant

    return drift_analysis


def compare_sessions(session1_path: Path, session2_path: Path) -> dict:
    """
    Compare epistemic patterns between two sessions (e.g., v1 vs v2).

    Args:
        session1_path: First session JSON
        session2_path: Second session JSON

    Returns:
        Comparison dict
    """
    drift1 = analyze_session_drift(session1_path)
    drift2 = analyze_session_drift(session2_path)

    if not drift1 or not drift2:
        return None

    comparison = {
        'session1': {
            'file': str(session1_path),
            'dominant_type': drift1['summary']['dominant_type'],
            'drift_detected': drift1['summary']['drift_detected']
        },
        'session2': {
            'file': str(session2_path),
            'dominant_type': drift2['summary']['dominant_type'],
            'drift_detected': drift2['summary']['drift_detected']
        },
        'stability_change': {
            'improved': False,
            'degraded': False,
            'notes': []
        }
    }

    # Analyze stability change
    if drift1['summary']['drift_detected'] and not drift2['summary']['drift_detected']:
        comparison['stability_change']['improved'] = True
        comparison['stability_change']['notes'].append(
            "Session 2 shows improved stability (no drift)"
        )

    if not drift1['summary']['drift_detected'] and drift2['summary']['drift_detected']:
        comparison['stability_change']['degraded'] = True
        comparison['stability_change']['notes'].append(
            "Session 2 shows degraded stability (new drift)"
        )

    # Type shift
    if drift1['summary']['dominant_type'] != drift2['summary']['dominant_type']:
        comparison['stability_change']['notes'].append(
            f"Type shift: {drift1['summary']['dominant_type']} → {drift2['summary']['dominant_type']}"
        )

    return comparison


def print_drift_report(drift_analysis: dict):
    """Print readable drift report."""
    print("\n" + "="*70)
    print("EPISTEMIC DRIFT ANALYSIS")
    print("="*70)
    print(f"\nSession: {drift_analysis['session_file']}")
    print(f"Start Time: {drift_analysis['session_start']}")

    summary = drift_analysis['summary']
    print(f"\n📊 Summary:")
    print(f"  Drift Detected: {'YES' if summary['drift_detected'] else 'NO'}")
    print(f"  Stable Mirrors: {summary['stable_mirrors']}")
    print(f"  Drifting Mirrors: {summary['drifting_mirrors']}")
    if summary['dominant_type'] is not None:
        print(f"  Dominant Type: {summary['dominant_type']}")

    print(f"\n🔍 Per-Mirror Analysis:")
    for mirror_id, data in drift_analysis['mirrors'].items():
        status = "⚠️  DRIFT" if data['drift_detected'] else "✓ STABLE"
        print(f"\n  {status} {mirror_id}")
        print(f"    Pattern: {data['drift_pattern']}")
        print(f"    Mean Ratio: {data['mean_ratio']:.2f}")
        print(f"    Ratio Range: {data['ratio_range'][0]:.2f} - {data['ratio_range'][1]:.2f}")


def print_comparison_report(comparison: dict):
    """Print session comparison report."""
    print("\n" + "="*70)
    print("SESSION COMPARISON")
    print("="*70)

    print("\n📄 Session 1:")
    print(f"  File: {comparison['session1']['file']}")
    print(f"  Dominant Type: {comparison['session1']['dominant_type']}")
    print(f"  Drift: {'YES' if comparison['session1']['drift_detected'] else 'NO'}")

    print("\n📄 Session 2:")
    print(f"  File: {comparison['session2']['file']}")
    print(f"  Dominant Type: {comparison['session2']['dominant_type']}")
    print(f"  Drift: {'YES' if comparison['session2']['drift_detected'] else 'NO'}")

    change = comparison['stability_change']
    print("\n📈 Stability Change:")
    if change['improved']:
        print("  ✅ IMPROVED - Session 2 more stable")
    elif change['degraded']:
        print("  ⚠️  DEGRADED - Session 2 less stable")
    else:
        print("  ≈ NO CHANGE")

    if change['notes']:
        print("\n📝 Notes:")
        for note in change['notes']:
            print(f"  - {note}")


def main():
    parser = argparse.ArgumentParser(
        description="Epistemic Drift Logger - Track topology stability over time",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('session_dir', nargs='?', help='Vault directory or session file')
    parser.add_argument('--compare', nargs=2, metavar=('SESSION1', 'SESSION2'),
                        help='Compare two sessions')
    parser.add_argument('--all-sessions', action='store_true',
                        help='Analyze all sessions in directory')

    args = parser.parse_args()

    if args.compare:
        # Compare two sessions
        session1 = Path(args.compare[0])
        session2 = Path(args.compare[1])

        comparison = compare_sessions(session1, session2)
        if comparison:
            print_comparison_report(comparison)
        else:
            print("✗ Could not load sessions for comparison")
        return

    if not args.session_dir:
        parser.print_help()
        return

    session_path = Path(args.session_dir)

    if session_path.is_file() and session_path.suffix == '.json':
        # Single session file
        drift = analyze_session_drift(session_path)
        if drift:
            print_drift_report(drift)
        else:
            print(f"✗ Could not load session: {session_path}")
        return

    if session_path.is_dir() and args.all_sessions:
        # Analyze all sessions in directory
        session_files = sorted(session_path.glob('session_*.json'))

        if not session_files:
            print(f"✗ No session files found in {session_path}")
            return

        print(f"\n📁 Found {len(session_files)} session(s) in {session_path}\n")

        for session_file in session_files:
            drift = analyze_session_drift(session_file)
            if drift:
                print_drift_report(drift)
        return

    # Default: try as session file
    if session_path.is_file():
        drift = analyze_session_drift(session_path)
        if drift:
            print_drift_report(drift)
    else:
        print(f"✗ Not a valid session file or directory: {session_path}")
        parser.print_help()


if __name__ == "__main__":
    main()
