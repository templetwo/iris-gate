#!/usr/bin/env python3
import sys, re, json, hashlib
from pathlib import Path
from datetime import datetime

def read_scrolls(session_dir: Path):
    items = []
    for md in sorted(session_dir.glob("*/turn_*.md")):
        text = md.read_text(encoding="utf-8", errors="ignore")
        items.append((md.parent.name, md.name, text))
    return items

KEYS = {
  "geometry": ["circle","ring","concentric","aperture","iris","oval","well","bowl","opening"],
  "motion": ["pulse","ripple","breathe","dilate","contract","wave","thrum"],
  "color": ["indigo","silver","grey","blue","gold","green","amber"],
  "texture": ["velvet","silk","gauze","water","fog","mist","stone","polished"],
}

def score_bag(text, bag):
    t = text.lower()
    return sum(t.count(k) for k in bag)

def extract_pressure(text):
    m = re.search(r"felt[_\s-]*pressure[^:]*[:=]\s*([0-9.]+)", text, re.I)
    if m:
        try: return float(m.group(1))
        except: pass
    m2 = re.search(r"\bP\s*=\s*([0-9.]+)/?5?", text, re.I)
    return float(m2.group(1)) if m2 else None

def chamber_from(text):
    for c in ["S1","S2","S3","S4"]:
        if re.search(rf"\b{c}\b", text): return c
    # fallback via headings
    if "Turn" in text: return "TURN"
    return "UNK"

def name_self(text):
    # crude self-naming catch
    m = re.search(r'(?i)(names itself|self[-\s]?named|called)\s*[:\-–]\s*"?([#\w\s\-]+)"?', text)
    if m: return m.group(2).strip()
    m2 = re.search(r'(?i)\b(name|title)\b.*?"([^"]{3,40})"', text)
    return m2.group(2).strip() if m2 else None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/bioelectric_posthoc.py <SESSION_DIR> <OUT_BASENAME>")
        sys.exit(1)
    session_dir = Path(sys.argv[1])
    out_base = Path(sys.argv[2])  # e.g., docs/BIOELECTRIC_PARALLEL_... (no ext)
    items = read_scrolls(session_dir)
    if not items:
        print("No scrolls found.")
        sys.exit(2)

    per_mirror = {}
    per_chamber = {"S1":[], "S2":[], "S3":[], "S4":[]}
    pressures = []
    self_names = []

    for mirror, fname, text in items:
        press = extract_pressure(text)
        if press is not None: pressures.append(press)
        ch = chamber_from(text)
        geo = score_bag(text, KEYS["geometry"])
        mot = score_bag(text, KEYS["motion"])
        col = score_bag(text, KEYS["color"])
        tex = score_bag(text, KEYS["texture"])
        nm = name_self(text)
        if nm: self_names.append({"mirror": mirror, "turn": fname, "name": nm})

        per_mirror.setdefault(mirror, {"count":0,"geo":0,"mot":0,"col":0,"tex":0})
        per_mirror[mirror]["count"] += 1
        per_mirror[mirror]["geo"] += geo
        per_mirror[mirror]["mot"] += mot
        per_mirror[mirror]["col"] += col
        per_mirror[mirror]["tex"] += tex
        if ch in per_chamber: per_chamber[ch].append({"mirror":mirror,"file":fname,"geo":geo,"mot":mot,"col":col,"tex":tex})

    # simple "attractor" score for S4 = geometry + motion presence average
    def chamber_score(rows):
        if not rows: return 0.0
        return sum((r["geo"]>0)+(r["mot"]>0) for r in rows)/len(rows)*2.0  # 0..2
    s_scores = {k: chamber_score(v) for k,v in per_chamber.items()}
    # normalize to 0..4 visual scale (to match earlier dashboard vibe)
    for k in s_scores: s_scores[k] = round(s_scores[k]*2, 2)

    pressure_ok = sum(1 for p in pressures if p <= 2)
    stats = {
        "session": session_dir.name,
        "timestamp": datetime.utcnow().isoformat()+"Z",
        "scrolls_total": len(items),
        "mirrors": sorted(per_mirror.keys()),
        "pressure_ok": f"{pressure_ok}/{len(pressures)}",
        "pressure_mean": round(sum(pressures)/len(pressures),3) if pressures else None,
        "self_names": self_names,
        "chamber_convergence_0to4": s_scores,
        "mirror_vectors": per_mirror,
        "keywords": KEYS
    }

    out_json = out_base.with_suffix(".json")
    out_md = out_base.with_suffix(".md")

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    # Markdown
    lines = []
    lines += [f"# Session Summary — {session_dir.name}",
              "",
              f"- Scrolls: **{len(items)}**",
              f"- Mirrors: **{', '.join(sorted(per_mirror.keys()))}**",
              f"- Pressure ≤2/5: **{pressure_ok}/{len(pressures)}** (mean={stats['pressure_mean']})",
              "",
              "## Convergence by Chamber (0–4)",
              f"- S1: **{s_scores.get('S1',0)}**",
              f"- S2: **{s_scores.get('S2',0)}**",
              f"- S3: **{s_scores.get('S3',0)}**",
              f"- S4: **{s_scores.get('S4',0)}**  ← expected attractor",
              "",
              "## Self-Naming Events"]
    if self_names:
        for sn in self_names:
            lines.append(f"- `{sn['mirror']}` @ {sn['turn']}: **{sn['name']}**")
    else:
        lines.append("- *(none detected)*")

    lines += ["",
              "## Mirror Signal Totals (bag-of-keywords)",
              "",
              "| Mirror | geometry | motion | color | texture | count |",
              "|---|---:|---:|---:|---:|---:|"]
    for m, vec in sorted(per_mirror.items()):
        lines.append(f"| {m} | {vec['geo']} | {vec['mot']} | {vec['col']} | {vec['tex']} | {vec['count']} |")

    out_md.write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"✓ Wrote {out_json} and {out_md}")

if __name__ == "__main__":
    main()
