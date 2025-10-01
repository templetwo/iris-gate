#!/usr/bin/env python3
"""
Enhanced convergence analyzer with S4 attractor ratios and evidence export.

Usage:
    python3 scripts/convergence_metrics.py <SESSION_DIR> [--explain] [--json OUTPUT.json]

Features:
    - Per-chamber S4 attractor ratio (% of turns with full GMA signature)
    - --explain: show which keywords fired per chamber
    - --json: export metrics for downstream analysis
"""
import sys, re, json
from pathlib import Path
from collections import defaultdict

# S4 attractor keyword families (config-ready)
S4_KEYWORDS = {
    "rhythm": ["rhythm", "pulsing", "reciprocal", "pulse", "waves", "thrum", "steady pulse", "ripples"],
    "center": ["luminous", "core", "center", "steady", "anchor", "still point", "beacon", "glow", "holds"],
    "aperture": ["aperture", "opening", "widening", "soften", "inviting", "bloom", "breathing open", "dilate", "expansion", "pull"]
}

GEO_KEYWORDS = ["ring", "concentric", "aperture", "iris", "circle", "well", "opening", "oval", "core", "center"]
MOT_KEYWORDS = ["pulse", "pulsing", "ripple", "breathe", "dilate", "dilation", "contract", "contraction", "wave", "thrum", "expand", "reciprocal"]

def mark(text, explain=False):
    """Detect geometry, motion, and S4 attractor signals."""
    t = text.lower()

    geo = any(k in t for k in GEO_KEYWORDS)
    mot = any(k in t for k in MOT_KEYWORDS)

    s4_rhythm = any(k in t for k in S4_KEYWORDS["rhythm"])
    s4_center = any(k in t for k in S4_KEYWORDS["center"])
    s4_aperture = any(k in t for k in S4_KEYWORDS["aperture"])
    s4_attractor = s4_rhythm and s4_center and s4_aperture

    if explain:
        evidence = {
            "rhythm": [k for k in S4_KEYWORDS["rhythm"] if k in t],
            "center": [k for k in S4_KEYWORDS["center"] if k in t],
            "aperture": [k for k in S4_KEYWORDS["aperture"] if k in t]
        }
        return ("G" if geo else "."), ("M" if mot else "."), ("A" if s4_attractor else "."), evidence

    return ("G" if geo else "."), ("M" if mot else "."), ("A" if s4_attractor else ".")

def chamber(text):
    """Extract chamber from header field or title."""
    # Read Chamber field from header (line 4: **Chamber:** S4)
    match = re.search(r'^\*\*Chamber:\*\*\s+(S[1-4])', text, re.MULTILINE)
    if match:
        return match.group(1)
    # Fallback: check title line (# Bioelectric Turn X • S4)
    match = re.search(r'#.*•\s+(S[1-4])', text)
    if match:
        return match.group(1)
    return "UNK"

def analyze(session_dir, explain=False):
    """Analyze session and compute per-mirror, per-chamber metrics."""
    root = Path(session_dir)
    mirrors = sorted({p.parent.name for p in root.glob("*/turn_*.md")})

    # Aggregate signals per chamber (OR across all turns)
    rows = {m: {f'S{i}': {"G": False, "M": False, "A": False, "turns": [], "attractor_turns": []}
                for i in range(1, 5)} for m in mirrors}

    for md in root.glob("*/turn_*.md"):
        m = md.parent.name
        t = md.read_text(errors="ignore")
        ch = chamber(t)

        if explain:
            g, mot, att, evidence = mark(t, explain=True)
        else:
            g, mot, att = mark(t)
            evidence = None

        if ch in rows[m]:
            rows[m][ch]["G"] |= (g == "G")
            rows[m][ch]["M"] |= (mot == "M")
            rows[m][ch]["A"] |= (att == "A")
            rows[m][ch]["turns"].append(md.name)
            if att == "A":
                rows[m][ch]["attractor_turns"].append((md.name, evidence if explain else None))

    # Compute S4 attractor ratio
    metrics = {}
    for m in mirrors:
        s4_total = len(rows[m]["S4"]["turns"])
        s4_attractor_count = len(rows[m]["S4"]["attractor_turns"])
        s4_ratio = s4_attractor_count / s4_total if s4_total > 0 else 0.0

        metrics[m] = {
            "chambers": {ch: {
                "geometry": rows[m][ch]["G"],
                "motion": rows[m][ch]["M"],
                "attractor": rows[m][ch]["A"],
                "total_turns": len(rows[m][ch]["turns"]),
                "attractor_turns": len(rows[m][ch]["attractor_turns"])
            } for ch in rows[m]},
            "s4_attractor_ratio": s4_ratio
        }

    return rows, metrics

def print_table(rows, metrics, explain=False):
    """Print convergence table with S4 attractor ratios."""
    print("Mirror                        S1   S2   S3   S4   S4_ratio")
    print("------------------------------------------------------------")
    print("Legend: G=geometry, M=motion, A=S4-attractor")
    print("------------------------------------------------------------")

    for m in sorted(rows.keys()):
        r = rows[m]
        s1_str = ("G" if r['S1']["G"] else ".") + ("M" if r['S1']["M"] else ".") + ("A" if r['S1']["A"] else ".")
        s2_str = ("G" if r['S2']["G"] else ".") + ("M" if r['S2']["M"] else ".") + ("A" if r['S2']["A"] else ".")
        s3_str = ("G" if r['S3']["G"] else ".") + ("M" if r['S3']["M"] else ".") + ("A" if r['S3']["A"] else ".")
        s4_str = ("G" if r['S4']["G"] else ".") + ("M" if r['S4']["M"] else ".") + ("A" if r['S4']["A"] else ".")
        s4_ratio = metrics[m]["s4_attractor_ratio"]

        print(f"{m:28s}  {s1_str:3s}  {s2_str:3s}  {s3_str:3s}  {s4_str:3s}  {s4_ratio:4.2f}")

    if explain:
        print("\n" + "="*60)
        print("S4 ATTRACTOR EVIDENCE")
        print("="*60)
        for m in sorted(rows.keys()):
            if rows[m]["S4"]["attractor_turns"]:
                print(f"\n{m}:")
                for turn, evidence in rows[m]["S4"]["attractor_turns"]:
                    if evidence:
                        print(f"  {turn}: rhythm={evidence['rhythm']}, center={evidence['center']}, aperture={evidence['aperture']}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    session_dir = sys.argv[1]
    explain = "--explain" in sys.argv
    json_output = None

    if "--json" in sys.argv:
        json_idx = sys.argv.index("--json")
        if json_idx + 1 < len(sys.argv):
            json_output = sys.argv[json_idx + 1]

    rows, metrics = analyze(session_dir, explain=explain)
    print_table(rows, metrics, explain=explain)

    if json_output:
        with open(json_output, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"\n✓ Metrics exported to {json_output}")

if __name__ == "__main__":
    main()
