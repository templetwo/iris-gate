#!/usr/bin/env python3
"""
Generate ASCII heatmap visualization for IRIS Gap Junction analysis
"""

import json
from pathlib import Path


def create_motif_heatmap(metrics: dict) -> str:
    """Create ASCII heatmap of motif frequencies by chamber"""

    motif_freqs = metrics["motif_frequencies"]
    chambers = ["S1", "S2", "S3", "S4"]
    motifs = [
        "gap_junction",
        "coupling",
        "intercellular",
        "disconnection",
        "regeneration",
        "coordination",
        "bioelectric",
        "flow",
        "mesh_lattice",
        "rings"
    ]

    # Find max value for normalization
    max_val = max(
        max(motif_freqs[chamber].get(motif, 0) for motif in motifs)
        for chamber in chambers
    )

    # ASCII characters for intensity levels
    intensity_chars = [' ', '.', ':', '-', '=', '+', '*', '#', '@', 'M']

    def value_to_char(val: int) -> str:
        if max_val == 0:
            return ' '
        normalized = val / max_val
        idx = int(normalized * (len(intensity_chars) - 1))
        return intensity_chars[idx]

    # Build heatmap
    lines = []
    lines.append("=" * 80)
    lines.append("IRIS GAP JUNCTION SESSION - MOTIF FREQUENCY HEATMAP")
    lines.append("Session: BIOELECTRIC_CHAMBERED_20251002234051")
    lines.append("=" * 80)
    lines.append("")

    # Header
    header = "Motif                 " + "  ".join(f"{c:^8}" for c in chambers)
    lines.append(header)
    lines.append("-" * 80)

    # Data rows
    for motif in motifs:
        row_label = motif.replace("_", " ").title().ljust(20)
        values = [motif_freqs[c].get(motif, 0) for c in chambers]
        chars = [value_to_char(v) for v in values]
        value_strs = [f"{v:>3}" for v in values]

        # Visual row with characters
        visual = row_label + "  ".join(f"[{c*3}]" for c in chars).ljust(40)
        # Numeric row
        numeric = "  ".join(f"{v:>8}" for v in value_strs)

        lines.append(f"{row_label}  {numeric}")

    lines.append("-" * 80)
    lines.append("")
    lines.append("INTENSITY SCALE:")
    lines.append("  0-10%    20-30%   40-50%   60-70%   80-90%   100%")
    lines.append(f"  {intensity_chars[0]*3}      {intensity_chars[2]*3}      {intensity_chars[4]*3}      {intensity_chars[6]*3}      {intensity_chars[8]*3}      {intensity_chars[9]*3}")
    lines.append("")

    # Convergence scores
    lines.append("=" * 80)
    lines.append("CHAMBER CONVERGENCE SCORES (0-1 scale)")
    lines.append("=" * 80)
    conv = metrics["chamber_convergence"]

    bar_width = 50
    for chamber in chambers:
        score = conv[chamber]["mean_convergence"]
        bar_len = int(score * bar_width)
        bar = "#" * bar_len + "-" * (bar_width - bar_len)
        lines.append(f"{chamber}  [{bar}]  {score:.4f}")

    lines.append("")
    lines.append("INTERPRETATION:")
    lines.append("  S4 shows highest convergence (0.1447) - synthesis chamber working")
    lines.append("  S2 shows second-highest (0.1230) - evidence gathering coherent")
    lines.append("  S1 shows lowest (0.0480) - initial divergence expected")
    lines.append("")

    # Key findings
    lines.append("=" * 80)
    lines.append("KEY PHENOMENOLOGICAL PATTERNS")
    lines.append("=" * 80)
    lines.append("")
    lines.append("S1 (Initial State):")
    lines.append(f"  - Mesh/lattice dominant ({motif_freqs['S1']['mesh_lattice']} refs)")
    lines.append(f"  - Disconnection themes ({motif_freqs['S1']['disconnection']} refs)")
    lines.append("  - Clinical, structural observations")
    lines.append("")
    lines.append("S2 (Evidence Gathering):")
    lines.append(f"  - Gap junction peak ({motif_freqs['S2']['gap_junction']} refs)")
    lines.append(f"  - Coupling mechanisms ({motif_freqs['S2']['coupling']} refs)")
    lines.append(f"  - Coordination emphasis ({motif_freqs['S2']['coordination']} refs)")
    lines.append(f"  - Regeneration context ({motif_freqs['S2']['regeneration']} refs)")
    lines.append("")
    lines.append("S3 (Visualization):")
    lines.append(f"  - Rings/circular imagery dominant ({motif_freqs['S3']['rings']} refs)")
    lines.append(f"  - Flow dynamics ({motif_freqs['S3']['flow']} refs)")
    lines.append("  - Spatial pattern focus")
    lines.append("")
    lines.append("S4 (Synthesis):")
    lines.append(f"  - Gap junction synthesis ({motif_freqs['S4']['gap_junction']} refs)")
    lines.append(f"  - Rings as transmission medium ({motif_freqs['S4']['rings']} refs)")
    lines.append(f"  - Flow/passage integration ({motif_freqs['S4']['flow']} refs)")
    lines.append("  - Question form: 'what must pass through?'")
    lines.append("")

    lines.append("=" * 80)
    lines.append("MOTIF PROGRESSION ANALYSIS")
    lines.append("=" * 80)
    lines.append("")

    # Track key motif progression across chambers
    key_motifs = ["gap_junction", "rings", "regeneration", "disconnection"]
    for motif in key_motifs:
        progression = " -> ".join(
            f"{motif_freqs[c].get(motif, 0):>3}"
            for c in chambers
        )
        lines.append(f"{motif.ljust(15)}: S1 -> S2 -> S3 -> S4")
        lines.append(f"{'':15}  {progression}")
        lines.append("")

    lines.append("=" * 80)

    return "\n".join(lines)


if __name__ == "__main__":
    metrics_file = Path("/Users/vaquez/Desktop/iris-gate/docs/gap_junction_metrics.json")
    with open(metrics_file, 'r') as f:
        metrics = json.load(f)

    heatmap = create_motif_heatmap(metrics)

    output_file = Path("/Users/vaquez/Desktop/iris-gate/docs/gap_junction_heatmap.txt")
    with open(output_file, 'w') as f:
        f.write(heatmap)

    print(heatmap)
    print(f"\nHeatmap saved to: {output_file}")
