#!/usr/bin/env python3
import sys, re
from pathlib import Path

def mark(text):
    t=text.lower()
    # Geometry: rings, apertures, iris, circles, openings
    geo=any(k in t for k in ["ring","concentric","aperture","iris","circle","well","opening","oval","core","center"])

    # Motion: pulsing, rippling, breathing, dilating, waves
    mot=any(k in t for k in ["pulse","pulsing","ripple","breathe","dilate","dilation","contract","contraction","wave","thrum","expand","reciprocal"])

    # S4-specific attractor signals: rhythm + center + aperture combined
    # Look for keywords anywhere in text (handles both prose and YAML)
    s4_rhythm=any(k in t for k in ["rhythm","pulsing","reciprocal","pulse","waves","thrum","steady pulse","ripples"])
    s4_center=any(k in t for k in ["luminous","core","center","steady","anchor","still point","beacon","glow","holds"])
    s4_aperture=any(k in t for k in ["aperture","opening","widening","soften","inviting","bloom","breathing open","dilate","expansion","pull"])
    s4_attractor = s4_rhythm and s4_center and s4_aperture

    return ("G" if geo else "."), ("M" if mot else "."), ("A" if s4_attractor else ".")

def chamber(text):
    # Read Chamber field from header (line 4: **Chamber:** S4)
    match = re.search(r'^\*\*Chamber:\*\*\s+(S[1-4])', text, re.MULTILINE)
    if match:
        return match.group(1)
    # Fallback: check title line (# Bioelectric Turn X • S4)
    match = re.search(r'#.*•\s+(S[1-4])', text)
    if match:
        return match.group(1)
    return "UNK"

root=Path(sys.argv[1])
mirrors=sorted({p.parent.name for p in root.glob("*/turn_*.md")})
# Aggregate signals: any turn showing the signal counts
rows={m:{'S1':{"G":False,"M":False,"A":False},'S2':{"G":False,"M":False,"A":False},
         'S3':{"G":False,"M":False,"A":False},'S4':{"G":False,"M":False,"A":False}} for m in mirrors}
for md in root.glob("*/turn_*.md"):
    m=md.parent.name
    t=md.read_text(errors="ignore")
    ch=chamber(t)
    g,mot,att=mark(t)
    if ch in rows[m]:
        rows[m][ch]["G"] |= (g == "G")
        rows[m][ch]["M"] |= (mot == "M")
        rows[m][ch]["A"] |= (att == "A")

print("Mirror                        S1   S2   S3   S4")
print("------------------------------------------------")
print("Legend: G=geometry, M=motion, A=S4-attractor")
print("------------------------------------------------")
for m in mirrors:
    r=rows[m]
    s1_str = ("G" if r['S1']["G"] else ".") + ("M" if r['S1']["M"] else ".") + ("A" if r['S1']["A"] else ".")
    s2_str = ("G" if r['S2']["G"] else ".") + ("M" if r['S2']["M"] else ".") + ("A" if r['S2']["A"] else ".")
    s3_str = ("G" if r['S3']["G"] else ".") + ("M" if r['S3']["M"] else ".") + ("A" if r['S3']["A"] else ".")
    s4_str = ("G" if r['S4']["G"] else ".") + ("M" if r['S4']["M"] else ".") + ("A" if r['S4']["A"] else ".")
    print(f"{m:28s}  {s1_str:3s}  {s2_str:3s}  {s3_str:3s}  {s4_str:3s}")
