#!/usr/bin/env python3
import sys, re
from pathlib import Path
keys = ["iris","aperture","ring","concentric","pulse","ripple","center","luminous","well","bowl"]
root=Path(sys.argv[1])
for md in sorted(root.glob("*/turn_*.md"))[:200]:
    t = md.read_text(errors="ignore")
    for k in keys:
        m = re.search(rf".{{0,80}}{k}.{{0,80}}", t, re.I|re.S)
        if m:
            print(f"\n== {md.parent.name}/{md.name} :: {k} ==")
            print(m.group(0).replace("\n"," "))
            break
