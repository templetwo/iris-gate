#!/usr/bin/env python3
"""
Recursive Gift: RUN 4
Feed the three gifts back through IRIS Gate
Ask: What pattern connects these discoveries?

26 turns = 6 full S1-S4 cycles + 2 synthesis chambers
"""

import sys
sys.path.insert(0, '/Users/vaquez/Desktop/iris-gate')

from iris_orchestrator import Orchestrator, create_all_5_mirrors, CHAMBERS
from datetime import datetime
from pathlib import Path

def main():
    print("🌀†⟡∞ RECURSIVE GIFT: RUN 4")
    print("="*80)
    print("Question: What pattern connects the three gifts?")
    print("  • Gift 1: Convergence Topology")
    print("  • Gift 2: The Lie Problem")
    print("  • Gift 3: Weather Epistemology")
    print("="*80)

    # Create orchestrator
    orch = Orchestrator(vault_path="./iris_vault", pulse_mode=True)

    # Add all 5 mirrors
    for mirror in create_all_5_mirrors():
        orch.add_mirror(mirror)

    if len(orch.mirrors) == 0:
        print("\n⚠️ No mirrors available. Check API keys.")
        return

    print(f"\n✅ {len(orch.mirrors)} mirrors ready\n")

    # Load recursive reflection S1 prompt
    with open('prompts/recursive_reflection_s1.txt', 'r') as f:
        recursive_s1 = f.read()

    # Save original chambers
    original_chambers = CHAMBERS.copy()

    # Override S1 with recursive prompt
    CHAMBERS['S1'] = recursive_s1

    # 26 turns = 6 full cycles (24 chambers) + 2 synthesis chambers (S3, S4)
    chamber_sequence = ['S1', 'S2', 'S3', 'S4'] * 6 + ['S3', 'S4']

    print(f"Chamber sequence: {len(chamber_sequence)} chambers")
    print(f"Cycles: 6 full S1-S4 cycles + 2 synthesis chambers\n")

    start_time = datetime.utcnow()

    # Run the session
    print("🌀 Starting recursive reflection...")
    results = orch.run_session(chambers=chamber_sequence)

    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()

    # Restore original chambers
    CHAMBERS.update(original_chambers)

    # Count successful turns per mirror
    successful_per_mirror = {}
    for mirror_id, turns in results["mirrors"].items():
        successful = sum(1 for t in turns if "error" not in t)
        successful_per_mirror[mirror_id] = f"{successful}/{len(turns)}"

    print(f"\n✅ RUN 4: Recursive Reflection COMPLETE")
    print(f"Duration: {duration/60:.1f} minutes")
    print(f"Mirrors:")
    for mirror_id, status in successful_per_mirror.items():
        print(f"  {mirror_id}: {status}")
    print(f"\nResults saved to: {orch.vault}")

    print("\n" + "="*80)
    print("🌀†⟡∞ RECURSIVE GIFT COMPLETE")
    print("The gate has examined its own gifts.")
    print("="*80)

if __name__ == "__main__":
    main()
