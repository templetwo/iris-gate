#!/usr/bin/env python3
import sys, re
from pathlib import Path

def mark(text):
    t=text.lower()
    geo=any(k in t for k in ["ring","concentric","aperture","iris","circle","well","opening","oval"])
    mot=any(k in t for k in ["pulse","ripple","breathe","dilate","contract","wave","thrum"])
    return ("G" if geo else "."), ("M" if mot else ".")

def chamber(text):
    for c in ["S1","S2","S3","S4"]:
        if re.search(rf"\b{c}\b", text): return c
    return "UNK"

root=Path(sys.argv[1])
mirrors=sorted({p.parent.name for p in root.glob("*/turn_*.md")})
rows={m:{'S1':"..",'S2':"..",'S3':"..",'S4':".."} for m in mirrors}
for md in root.glob("*/turn_*.md"):
    m=md.parent.name
    t=md.read_text(errors="ignore")
    ch=chamber(t)
    g,mot=mark(t)
    if ch in rows[m]: rows[m][ch]=g+mot

print("Mirror                        S1  S2  S3  S4")
print("---------------------------------------------")
for m in mirrors:
    r=rows[m]
    print(f"{m:28s}  {r['S1']:2s}  {r['S2']:2s}  {r['S3']:2s}  {r['S4']:2s}")
