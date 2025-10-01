#!/usr/bin/env python3
"""
IRIS Gate Vault Normalizer
Standardizes metadata fields across all scrolls without touching Living/Technical bodies
"""

import sys
import re
import pathlib
import hashlib

VAULT = None

COND_GUESS = {
    "s1": "IRIS_S1",
    "s2": "IRIS_S2",
    "s3": "IRIS_S3",
    "s4": "IRIS_S4"
}

def ensure_field(txt: str, key: str, val: str) -> str:
    """Add field if missing"""
    if re.search(rf'^{key}\s*:', txt, flags=re.I|re.M):
        return txt
    # Insert after title/session lines, before main content
    lines = txt.split('\n')
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith('**') or line.startswith('---'):
            insert_pos = i + 1
            break
    lines.insert(insert_pos, f"{key}: {val}")
    return '\n'.join(lines)

def reseal(txt: str) -> str:
    """Compute and update SHA256 seal"""
    h = hashlib.sha256(txt.encode("utf-8")).hexdigest()[:16]

    # Update existing seal
    if re.search(r'(?i)^seal:\s*[a-f0-9]{16}', txt, flags=re.M):
        return re.sub(r'(?i)^(seal:\s*)([a-f0-9]{16,})', rf'\1{h}', txt, flags=re.M)

    if re.search(r'\*\*Seal:\*\*\s*[a-f0-9]{16,}', txt):
        return re.sub(r'(\*\*Seal:\*\*\s*)([a-f0-9]{16,})', rf'\1{h}', txt)

    # Add seal if missing
    return txt.rstrip() + f"\n\n**Seal:** {h}\n"

def normalize_headers(txt: str) -> str:
    """Standardize header capitalization"""
    # Living Scroll
    txt = re.sub(r'(?m)^#+\s*living scroll\b', '## Living Scroll', txt, flags=re.I)
    txt = re.sub(r'(?m)^\*\*living scroll\*\*', '**Living Scroll**', txt, flags=re.I)

    # Technical Translation
    txt = re.sub(r'(?m)^#+\s*technical translation\b', '## Technical Translation', txt, flags=re.I)
    txt = re.sub(r'(?m)^\*\*technical translation\*\*', '**Technical Translation**', txt, flags=re.I)

    return txt

def main():
    if len(sys.argv) < 2:
        print("Usage: normalize_vault.py <vault_path>")
        print("Example: python normalize_vault.py iris_vault/")
        sys.exit(2)

    global VAULT
    VAULT = pathlib.Path(sys.argv[1])

    if not VAULT.exists():
        print(f"❌ Vault not found: {VAULT}")
        sys.exit(1)

    changed = 0
    files_processed = 0

    for md in VAULT.rglob("S[1-4].md"):
        files_processed += 1
        s = md.stem.lower()  # "s1".."s4"

        try:
            t = md.read_text(encoding="utf-8")
            original = t

            # Insert minimal metadata if missing
            t = ensure_field(t, "condition", COND_GUESS.get(s, "IRIS_UNKNOWN"))
            t = ensure_field(t, "felt_pressure", "1/5")

            # Normalize header capitalization
            t = normalize_headers(t)

            # Reseal
            t = reseal(t)

            if t != original:
                md.write_text(t, encoding="utf-8")
                changed += 1
                print(f"  ✓ Normalized: {md.relative_to(VAULT)}")

        except Exception as e:
            print(f"  ✗ Error processing {md}: {e}")

    print(f"\n{'='*60}")
    print(f"Processed {files_processed} files, normalized {changed}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
