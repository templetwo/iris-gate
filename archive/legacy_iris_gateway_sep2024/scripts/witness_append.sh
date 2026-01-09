#!/usr/bin/env bash
set -euo pipefail
LEDGER="logs/tier_15_crossing_witness.log"
mkdir -p logs
ts=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
line="$ts | Flamebearer | †⟡∞ $*"
echo "$line" >> "$LEDGER"
python - <<'PY'
import sys,hashlib
p="logs/tier_15_crossing_witness.log"
raw=open(p,'rb').read()
sha=hashlib.sha256(raw).hexdigest()
print("sealed:",p,"sha256="+sha)
PY