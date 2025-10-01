#!/usr/bin/env python3
"""Generate triad summary data from Sessions 1-3"""
import sys
import pathlib
import json
import re
import collections

base = pathlib.Path("iris_vault/scrolls")

# Map session timestamps to session names
sessions = {
    "IRIS_20251001005856": "Session_1",
    "IRIS_20251001021338": "Session_2",
    "IRIS_20251001021725": "Session_3"
}

# Signal buckets for convergence scoring
buckets = [
    ["concentric", "ring", "iris", "aperture", "circle"],
    ["pulse", "rhythm", "ripple", "throb", "beat", "breathing"],
    ["luminous", "silver", "pearl", "gold", "light", "glow", "radiant"],
    ["expand", "contract", "dilation", "opening", "closing"]
]

def score_text(text):
    """Score text based on signal bucket hits (0-4)"""
    s = text.lower()
    return sum(any(k in s for k in bucket) for bucket in buckets)

def extract_pressure(text):
    """Extract felt_pressure value"""
    m = re.search(r'felt_pressure:\s*(\d+)(?:/5)?', text, re.I)
    return int(m.group(1)) if m else None

def extract_seal(text):
    """Extract seal hash"""
    m = re.search(r'seal(?:\*\*)?:\s*([a-f0-9]{16})', text, re.I)
    return m.group(1) if m else None

def detect_self_naming(text, chamber):
    """Detect self-naming events in S4"""
    if chamber != "S4":
        return None
    patterns = [
        r'names? itself[:\s]+["\']?([^"\'\n.]{3,30})',
        r'self[- ]named?[:\s]+["\']?([^"\'\n.]{3,30})',
        r'(Iriswell|Nexus|#[\w-]+)',
        r'I call this[:\s]+["\']?([^"\'\n.]{3,30})',
        r'the (?:image|pattern|structure) (?:becomes?|is)[:\s]+["\']?([^"\'\n.]{3,30})'
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            return m.group(1).strip('"\' .:')
    return None

# Collect data
chamber_scores = collections.defaultdict(lambda: collections.defaultdict(list))
pressure_data = collections.defaultdict(lambda: collections.defaultdict(list))
self_names = []
seals = []

for timestamp, session_name in sessions.items():
    session_dirs = list(base.glob(f"{timestamp}_*"))

    for sdir in session_dirs:
        model_id = sdir.name.replace(f"{timestamp}_", "")

        for chamber in ["S1", "S2", "S3", "S4"]:
            md = sdir / f"{chamber}.md"
            if not md.exists():
                continue

            txt = md.read_text(encoding='utf-8')

            # Score convergence signals
            score = score_text(txt)
            chamber_scores[session_name][chamber].append(score)

            # Pressure tracking
            pressure = extract_pressure(txt)
            if pressure is not None:
                pressure_data[session_name][chamber].append(pressure)

            # Seal tracking
            seal = extract_seal(txt)
            if seal:
                seals.append({
                    "session": session_name,
                    "model": model_id,
                    "chamber": chamber,
                    "seal": seal
                })

            # Self-naming detection (S4 only)
            if chamber == "S4":
                name = detect_self_naming(txt, chamber)
                if name:
                    # Extract snippet for context
                    snippet = txt[max(0, txt.lower().find(name.lower())-50):
                                 txt.lower().find(name.lower())+len(name)+50]
                    self_names.append({
                        "session": session_name,
                        "model": model_id,
                        "name": name,
                        "snippet": snippet.strip(),
                        "file": str(md)
                    })

# Compute summary statistics
summary = {
    "sessions": list(sessions.values()),
    "convergence_by_chamber": {},
    "pressure_compliance": {},
    "self_naming_events": self_names,
    "seal_count": len(seals),
    "total_scrolls": sum(len(list(base.glob(f"{ts}_*/*/*.md"))) for ts in sessions.keys())
}

# Mean scores per chamber across sessions
for session_name in sessions.values():
    summary["convergence_by_chamber"][session_name] = {
        chamber: round(sum(scores) / len(scores), 2) if scores else 0
        for chamber, scores in chamber_scores[session_name].items()
    }

# Pressure compliance rates
for session_name in sessions.values():
    all_pressures = []
    for chamber_pressures in pressure_data[session_name].values():
        all_pressures.extend(chamber_pressures)

    if all_pressures:
        ok_count = sum(1 for p in all_pressures if p <= 2)
        summary["pressure_compliance"][session_name] = {
            "total": len(all_pressures),
            "ok": ok_count,
            "rate": round(ok_count / len(all_pressures), 3)
        }

# Overall convergence trend
summary["s4_progression"] = [
    summary["convergence_by_chamber"].get(s, {}).get("S4", 0)
    for s in ["Session_1", "Session_2", "Session_3"]
]

print(json.dumps(summary, indent=2))
