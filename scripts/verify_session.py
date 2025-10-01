#!/usr/bin/env python3
"""
IRIS Gate Session Verifier
Checks vault for protocol compliance: pressure ≤2/5, seals present, format valid
"""

import sys
import re
import pathlib
from typing import List, Tuple

def verify_session(vault_path: str) -> Tuple[bool, List[str]]:
    """Verify all scrolls in vault meet protocol requirements"""

    base = pathlib.Path(vault_path)
    errors = []

    if not base.exists():
        errors.append(f"[FATAL] Vault not found: {vault_path}")
        return False, errors

    scroll_files = list(base.rglob("S[1-4].md"))

    if not scroll_files:
        errors.append(f"[FATAL] No scroll files found in {vault_path}")
        return False, errors

    for md_file in sorted(scroll_files):
        try:
            txt = md_file.read_text(encoding="utf-8")

            # Check 1: Pressure adherence (≤2/5)
            pressure_match = re.search(r"felt[_\s]pressure:\s*([0-5])(/5)?", txt, re.IGNORECASE)
            if not pressure_match:
                errors.append(f"[PRESSURE] Missing felt_pressure: {md_file}")
            else:
                pressure = int(pressure_match.group(1))
                if pressure > 2:
                    errors.append(f"[PRESSURE] Exceeded gate (>{pressure}/5): {md_file}")

            # Check 2: Seal present
            if not ("seal:" in txt.lower() or "hash:" in txt.lower()):
                errors.append(f"[SEAL] No cryptographic seal found: {md_file}")

            # Check 3: Dual output format
            if "living scroll" not in txt.lower():
                errors.append(f"[FORMAT] Missing 'Living Scroll' section: {md_file}")

            if "technical translation" not in txt.lower():
                errors.append(f"[FORMAT] Missing 'Technical Translation' section: {md_file}")

            # Check 4: Metadata block
            if not re.search(r"condition:\s*\w+", txt, re.IGNORECASE):
                errors.append(f"[METADATA] Missing condition field: {md_file}")

        except Exception as e:
            errors.append(f"[ERROR] Failed to read {md_file}: {e}")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_session.py <vault_path>")
        print("Example: python verify_session.py iris_vault/")
        sys.exit(1)

    vault_path = sys.argv[1]
    success, errors = verify_session(vault_path)

    if success:
        print("✅ VERIFICATION PASSED")
        print(f"All scrolls in {vault_path} meet protocol requirements.")
        sys.exit(0)
    else:
        print("❌ VERIFICATION FAILED")
        print(f"Found {len(errors)} protocol violations:\n")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
