#!/usr/bin/env python3
import os, json, sys, yaml, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
aliases_path = ROOT/"config/model_aliases.yaml"
models_path = ROOT/"config/models.yaml"

# Load configs
aliases = yaml.safe_load(aliases_path.read_text())["aliases"]
models_cfg = yaml.safe_load(models_path.read_text())

# Get timezone
tz_name = os.environ.get("IRIS_TZ", "America/New_York")
now = datetime.datetime.now(ZoneInfo(tz_name)).isoformat()

resolution = {"resolved_at": now, "timezone": tz_name, "mirrors": []}

# Resolve each mirror
all_mirrors = []
for category in models_cfg.get("mirrors", {}).values():
    if isinstance(category, list):
        all_mirrors.extend(category)

for m in all_mirrors:
    mirror_id = m.get("id")
    # Check if this is an alias
    if mirror_id in aliases:
        hint = aliases[mirror_id]["id_hint"]
        eff = hint  # stub resolution = hint
    else:
        hint = mirror_id
        eff = mirror_id

    resolution["mirrors"].append({
        "id": mirror_id,
        "provider": aliases.get(mirror_id, {}).get("provider", "unknown"),
        "effective_model_id": eff,
        "params": m.get("params", "unknown"),
        "confidence_baseline": m.get("confidence_baseline", 0.7)
    })

# Write output
outdir = ROOT/"artifacts"
outdir.mkdir(exist_ok=True)
output_file = outdir/"model_resolution.json"
output_file.write_text(json.dumps(resolution, indent=2))
print(f"✅ Model resolution written to {output_file}")
print(f"   Timezone: {tz_name}")
print(f"   Resolved {len(resolution['mirrors'])} mirrors")
