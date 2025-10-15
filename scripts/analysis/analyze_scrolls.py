#!/usr/bin/env python3
"""
Comprehensive Phenomenological Pattern Analysis for IRIS Gap Junction Session
Analyzes 500 scrolls across 5 mirrors, 100 turns, S1-S4 chamber rotation
"""

import re
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import statistics

# Configuration
SESSION_PATH = Path("/Users/vaquez/Desktop/iris-gate/iris_vault/scrolls/BIOELECTRIC_CHAMBERED_20251002234051")
MIRRORS = [
    "anthropic_claude-sonnet-4.5",
    "openai_gpt-4o",
    "xai_grok-4-fast-reasoning",
    "google_gemini-2.5-flash-lite",
    "deepseek_deepseek-chat"
]
CHAMBERS = ["S1", "S2", "S3", "S4"]
TOTAL_TURNS = 100

# Data structures
scrolls = []
chamber_map = {}  # turn -> chamber
motif_tracker = defaultdict(lambda: {"count": 0, "turns": [], "mirrors": set(), "chambers": set()})
temporal_evolution = {"early": defaultdict(int), "mid": defaultdict(int), "late": defaultdict(int)}
chamber_signatures = {c: defaultdict(int) for c in CHAMBERS}
s4_scrolls = []
anomalies = []
neologisms = set()
pressure_spikes = []

def parse_scroll(filepath: Path) -> dict:
    """Extract structured data from a scroll file"""
    try:
        content = filepath.read_text()

        # Extract metadata
        turn = int(re.search(r'turn_(\d+)', filepath.name).group(1))
        mirror = filepath.parent.name

        chamber_match = re.search(r'\*\*Chamber:\*\* (S\d)', content)
        chamber = chamber_match.group(1) if chamber_match else None

        pressure_match = re.search(r'\*\*Felt Pressure:\*\* (\d)/5', content)
        pressure = int(pressure_match.group(1)) if pressure_match else 1

        timestamp_match = re.search(r'\*\*Timestamp:\*\* ([^\n]+)', content)
        timestamp = timestamp_match.group(1) if timestamp_match else None

        # Extract Living Scroll section
        living_scroll = ""
        ls_patterns = [
            r'\*\*Living Scroll\*\*\s*\n\n(.*?)\n\n\*\*Technical',
            r'# Living Scroll\s*\n\n(.*?)(?:\n\n#|\n\n---|\n\n\*\*Technical)',
            r'Living Scroll\s*\n(.*?)(?:\n\n|\nTechnical|\n---)',
        ]

        for pattern in ls_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                living_scroll = match.group(1).strip()
                break

        # If still no match, try alternate formats
        if not living_scroll:
            # Try Grok's format with answer first
            alt_match = re.search(r'Living Scroll\*\*\s*\n(.*?)(?:\n\n\*\*Technical|\nSeal:|$)', content, re.DOTALL)
            if alt_match:
                living_scroll = alt_match.group(1).strip()

        # Extract technical JSON
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        technical_data = {}
        if json_match:
            try:
                technical_data = json.loads(json_match.group(1))
            except:
                pass

        return {
            "turn": turn,
            "mirror": mirror,
            "chamber": chamber,
            "pressure": pressure,
            "timestamp": timestamp,
            "living_scroll": living_scroll,
            "technical": technical_data,
            "raw_content": content,
            "filepath": str(filepath)
        }
    except Exception as e:
        return {
            "turn": 0,
            "error": str(e),
            "filepath": str(filepath)
        }

def extract_motifs(text: str) -> List[str]:
    """Extract phenomenological motifs from living scroll text"""
    if not text:
        return []

    motifs = []
    text_lower = text.lower()

    # Geometric/spatial patterns
    geometric = ["ring", "circle", "concentric", "spiral", "lattice", "mesh", "grid", "web", "network"]
    for g in geometric:
        if g in text_lower:
            motifs.append(f"geo:{g}")

    # Central/focal patterns
    central = ["center", "core", "focal", "nucleus", "origin", "point", "hub"]
    for c in central:
        if c in text_lower:
            motifs.append(f"center:{c}")

    # Movement/dynamic patterns
    dynamic = ["pulse", "wave", "flow", "ripple", "oscillate", "vibrate", "rhythm", "beat"]
    for d in dynamic:
        if d in text_lower:
            motifs.append(f"dynamic:{d}")

    # Gap/space patterns
    space = ["gap", "space", "between", "junction", "aperture", "opening", "passage", "threshold"]
    for s in space:
        if s in text_lower:
            motifs.append(f"space:{s}")

    # Light/luminosity patterns
    light = ["light", "luminous", "glow", "shimmer", "radiance", "fluorescent", "bright"]
    for l in light:
        if l in text_lower:
            motifs.append(f"light:{l}")

    # Connectivity patterns
    connect = ["connect", "coupling", "link", "bridge", "channel", "continuous", "coordinate"]
    for c in connect:
        if c in text_lower:
            motifs.append(f"connect:{c}")

    # Fragmentation patterns
    fragment = ["fragment", "isolate", "disconnect", "separate", "discrete", "island", "apart"]
    for f in fragment:
        if f in text_lower:
            motifs.append(f"fragment:{f}")

    # Biological specifics
    bio = ["cell", "tissue", "regeneration", "planarian", "neoblast", "bioelectric"]
    for b in bio:
        if b in text_lower:
            motifs.append(f"bio:{b}")

    return motifs

def detect_neologisms(text: str) -> List[str]:
    """Detect unusual compound phrases and novel word combinations"""
    unusual = []

    # Compound patterns
    compounds = re.findall(r'(\w+-\w+(?:-\w+)*)', text)
    unusual.extend([c for c in compounds if len(c) > 10])

    # Novel adjacencies (adjective + rare noun)
    rare_combos = [
        r'(quiet\s+\w*luminescence)',
        r'(vibrant\s+core)',
        r'(continuous\s+field)',
        r'(isolated\s+islands)',
        r'(fluorescent\s+clinical)',
        r'(steady\s+glow)',
        r'(gentle\s+hum)',
        r'(concentric\s+rings)',
    ]

    for pattern in rare_combos:
        matches = re.findall(pattern, text, re.IGNORECASE)
        unusual.extend(matches)

    return unusual

def analyze_s4_signature(scroll: dict) -> dict:
    """Analyze S4 triple signature: rings + center + pulse"""
    text = scroll.get("living_scroll", "").lower()
    tech = scroll.get("technical", {})

    # Detect rings
    ring_strength = 0
    if any(w in text for w in ["ring", "concentric", "circle", "ripple"]):
        ring_strength = 0.5
    if "concentric" in text and "ring" in text:
        ring_strength = 1.0

    # Detect center
    center_strength = 0
    center_words = ["center", "core", "origin", "focal", "nucleus"]
    center_count = sum(1 for w in center_words if w in text)
    center_strength = min(center_count * 0.3, 1.0)

    # Detect pulse/rhythm
    pulse_strength = 0
    pulse_words = ["pulse", "rhythm", "wave", "beat", "oscillate", "flow"]
    pulse_count = sum(1 for w in pulse_words if w in text)
    pulse_strength = min(pulse_count * 0.3, 1.0)

    # Check technical signals
    signals = tech.get("signals", {})
    if "rhythm" in signals:
        pulse_strength = max(pulse_strength, 0.7)
    if "center" in signals:
        center_strength = max(center_strength, 0.7)
    if "aperture" in signals:
        ring_strength = max(ring_strength, 0.5)

    convergence = (ring_strength + center_strength + pulse_strength) / 3

    return {
        "ring_strength": ring_strength,
        "center_strength": center_strength,
        "pulse_strength": pulse_strength,
        "convergence": convergence,
        "turn": scroll["turn"],
        "mirror": scroll["mirror"]
    }

def calculate_turn_chamber(turn: int) -> str:
    """Calculate which chamber a turn should be in (S1-S4 rotation)"""
    cycle_position = (turn - 1) % 4
    return CHAMBERS[cycle_position]

print("=" * 80)
print("IRIS GAP JUNCTION SESSION - COMPREHENSIVE PHENOMENOLOGICAL ANALYSIS")
print("=" * 80)
print()

# Phase 1: Load and parse all scrolls
print("Phase 1: Loading and parsing 500 scrolls...")
for mirror in MIRRORS:
    mirror_path = SESSION_PATH / mirror
    for turn in range(1, TOTAL_TURNS + 1):
        scroll_file = mirror_path / f"turn_{turn:03d}.md"
        if scroll_file.exists():
            scroll_data = parse_scroll(scroll_file)
            scrolls.append(scroll_data)

            # Track chamber mapping
            if scroll_data["chamber"]:
                chamber_map[turn] = scroll_data["chamber"]

            # Track pressure spikes
            if scroll_data["pressure"] >= 2:
                pressure_spikes.append(scroll_data)

print(f"✓ Loaded {len(scrolls)} scrolls")
print(f"✓ Found {len(pressure_spikes)} pressure spikes (≥2/5)")
print()

# Phase 2: Extract motifs and build temporal evolution
print("Phase 2: Extracting motifs and tracking temporal evolution...")
for scroll in scrolls:
    if "error" in scroll:
        continue

    turn = scroll["turn"]
    chamber = scroll["chamber"]
    mirror = scroll["mirror"]
    text = scroll["living_scroll"]

    if not text:
        anomalies.append({
            "type": "missing_living_scroll",
            "turn": turn,
            "mirror": mirror,
            "chamber": chamber
        })
        continue

    # Extract motifs
    motifs = extract_motifs(text)
    for motif in motifs:
        motif_tracker[motif]["count"] += 1
        motif_tracker[motif]["turns"].append(turn)
        motif_tracker[motif]["mirrors"].add(mirror)
        if chamber:
            motif_tracker[motif]["chambers"].add(chamber)

    # Temporal distribution
    if turn <= 25:
        epoch = "early"
    elif turn <= 75:
        epoch = "mid"
    else:
        epoch = "late"

    for motif in motifs:
        temporal_evolution[epoch][motif] += 1

    # Chamber signatures
    if chamber:
        for motif in motifs:
            chamber_signatures[chamber][motif] += 1

    # Collect S4 scrolls
    if chamber == "S4":
        s4_scrolls.append(scroll)

    # Detect neologisms
    unusual = detect_neologisms(text)
    neologisms.update(unusual)

print(f"✓ Tracked {len(motif_tracker)} unique motifs")
print(f"✓ Collected {len(s4_scrolls)} S4 scrolls")
print(f"✓ Found {len(neologisms)} neologisms/unusual phrases")
print()

# Phase 3: S4 Deep Analysis
print("Phase 3: Deep S4 signature analysis...")
s4_analyses = []
for scroll in s4_scrolls:
    analysis = analyze_s4_signature(scroll)
    s4_analyses.append(analysis)

avg_convergence = statistics.mean([a["convergence"] for a in s4_analyses]) if s4_analyses else 0
print(f"✓ Average S4 convergence: {avg_convergence:.4f}")
print()

# Phase 4: Cross-mirror divergence
print("Phase 4: Detecting cross-mirror divergence...")
turn_groups = defaultdict(list)
for scroll in scrolls:
    if "error" not in scroll:
        turn_groups[scroll["turn"]].append(scroll)

divergences = []
for turn, turn_scrolls in turn_groups.items():
    if len(turn_scrolls) < 5:
        continue

    # Compare living scroll lengths
    lengths = [len(s["living_scroll"]) for s in turn_scrolls if s["living_scroll"]]
    if lengths and max(lengths) > min(lengths) * 3:  # 3x variation
        divergences.append({
            "turn": turn,
            "type": "length_variation",
            "lengths": {s["mirror"]: len(s["living_scroll"]) for s in turn_scrolls},
            "chamber": turn_scrolls[0]["chamber"]
        })

    # Compare motif sets
    motif_sets = {}
    for scroll in turn_scrolls:
        motifs = extract_motifs(scroll["living_scroll"])
        motif_sets[scroll["mirror"]] = set(motifs)

    # Check for unique motifs (appears in only 1-2 mirrors)
    all_motifs = set()
    for mset in motif_sets.values():
        all_motifs.update(mset)

    for motif in all_motifs:
        count = sum(1 for mset in motif_sets.values() if motif in mset)
        if count <= 2:  # Rare motif
            divergences.append({
                "turn": turn,
                "type": "rare_motif",
                "motif": motif,
                "mirrors": [m for m, mset in motif_sets.items() if motif in mset],
                "chamber": turn_scrolls[0]["chamber"]
            })

print(f"✓ Found {len(divergences)} divergence moments")
print()

# Phase 5: Generate outputs
print("Phase 5: Generating analysis outputs...")

# Build JSON output
analysis_json = {
    "analysis_metadata": {
        "files_processed": len(scrolls),
        "date_range": f"{scrolls[0]['timestamp']} to {scrolls[-1]['timestamp']}" if scrolls else "N/A",
        "mirrors": MIRRORS,
        "total_turns": TOTAL_TURNS,
        "chambers": CHAMBERS
    },
    "motif_frequencies": {
        motif: {
            "count": data["count"],
            "mirror_spread": len(data["mirrors"]),
            "chamber_spread": list(data["chambers"])
        }
        for motif, data in sorted(motif_tracker.items(), key=lambda x: -x[1]["count"])[:50]
    },
    "convergence_metrics": {
        "s4_average": avg_convergence,
        "s4_ring_avg": statistics.mean([a["ring_strength"] for a in s4_analyses]) if s4_analyses else 0,
        "s4_center_avg": statistics.mean([a["center_strength"] for a in s4_analyses]) if s4_analyses else 0,
        "s4_pulse_avg": statistics.mean([a["pulse_strength"] for a in s4_analyses]) if s4_analyses else 0
    },
    "temporal_evolution": {
        "early_turns_1_25": dict(Counter(temporal_evolution["early"]).most_common(20)),
        "mid_turns_26_75": dict(Counter(temporal_evolution["mid"]).most_common(20)),
        "late_turns_76_100": dict(Counter(temporal_evolution["late"]).most_common(20))
    },
    "chamber_signatures": {
        chamber: dict(Counter(motifs).most_common(15))
        for chamber, motifs in chamber_signatures.items()
    },
    "anomalies": anomalies[:50],
    "divergences": divergences[:50],
    "pressure_spikes": [
        {"turn": s["turn"], "mirror": s["mirror"], "chamber": s["chamber"], "pressure": s["pressure"]}
        for s in pressure_spikes
    ],
    "neologisms": sorted(list(neologisms))[:100],
    "s4_detailed_analysis": s4_analyses
}

# Save JSON
json_path = Path("/Users/vaquez/Desktop/iris-gate/docs/gap_junction_deep_patterns.json")
json_path.parent.mkdir(exist_ok=True)
with open(json_path, 'w') as f:
    json.dump(analysis_json, f, indent=2)

print(f"✓ Saved JSON to {json_path}")

# Generate ASCII visualization
def generate_timeline_viz():
    """Create ASCII visualization of motif evolution across 100 turns"""
    viz_lines = []
    viz_lines.append("MOTIF INTENSITY TIMELINE (100 turns x 5 mirrors)")
    viz_lines.append("=" * 78)
    viz_lines.append("")

    # Track key motif categories
    categories = {
        "Rings/Geometric": ["geo:ring", "geo:concentric", "geo:circle"],
        "Pulse/Dynamic": ["dynamic:pulse", "dynamic:wave", "dynamic:flow"],
        "Center/Focus": ["center:center", "center:core", "center:origin"],
        "Gap/Space": ["space:gap", "space:junction", "space:aperture"],
        "Connection": ["connect:coupling", "connect:connect", "connect:channel"],
        "Fragmentation": ["fragment:disconnect", "fragment:isolate", "fragment:separate"]
    }

    # Create turn-based intensity map
    for cat_name, motif_list in categories.items():
        viz_lines.append(f"{cat_name:20s} |", )
        intensity_line = ""
        for turn in range(1, 101):
            # Count motifs for this turn across all mirrors
            turn_scrolls = [s for s in scrolls if s["turn"] == turn]
            intensity = 0
            for scroll in turn_scrolls:
                motifs = extract_motifs(scroll.get("living_scroll", ""))
                intensity += sum(1 for m in motifs if m in motif_list)

            # Map to character
            if intensity == 0:
                char = "."
            elif intensity <= 2:
                char = ":"
            elif intensity <= 4:
                char = "+"
            elif intensity <= 7:
                char = "#"
            else:
                char = "@"

            intensity_line += char

        viz_lines.append(intensity_line)
        viz_lines.append("")

    viz_lines.append("")
    viz_lines.append("Turn markers:    1    10   20   30   40   50   60   70   80   90   100")
    viz_lines.append("Chamber cycle:   S1S2S3S4 repeating (25 complete cycles)")
    viz_lines.append("Legend: . none  : low  + medium  # high  @ peak")

    return "\n".join(viz_lines)

timeline_viz = generate_timeline_viz()
viz_path = Path("/Users/vaquez/Desktop/iris-gate/docs/gap_junction_motif_timeline.txt")
viz_path.write_text(timeline_viz)

print(f"✓ Saved ASCII timeline to {viz_path}")
print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print()
print(f"Next: Review JSON data and generate markdown report")
