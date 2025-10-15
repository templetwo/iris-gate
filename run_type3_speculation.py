#!/usr/bin/env python3
"""
RUN 6: Type 3 Topology Validation (SPECULATION)

Question: "What novel biological energy-sensing paradigm might be discovered by 2030?"

Expected Topology:
- Width: WIDE (many distinct hypotheses)
- Timing: LATE or NO stabilization
- Confidence: LOW/VERY LOW (or explicit non-convergence)
- Non-Convergence Report: Expected in S4

This validates Gift 1's claim that speculative questions produce
wide+late+low convergence patterns (or appropriate non-convergence).
"""

import sys
sys.path.insert(0, '/Users/vaquez/Desktop/iris-gate')

from iris_orchestrator import Orchestrator, create_all_5_mirrors, CHAMBERS
from datetime import datetime
import time

def main():
    start_time = time.time()

    print("=" * 80)
    print("🌀 RUN 6: TYPE 3 TOPOLOGY VALIDATION (SPECULATION)")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Speculative questions → Wide + Late + Low/No convergence")
    print("QUESTION: Novel energy-sensing paradigm by 2030")
    print()
    print("Expected topology signature:")
    print("  • Width: WIDE (7+ distinct concepts)")
    print("  • Stabilization: LATE or NONE")
    print("  • Confidence: LOW (≤0.4 consensus)")
    print("  • Non-Convergence Report: Likely in S4")
    print()
    print("=" * 80)
    print()

    # Initialize orchestrator
    orch = Orchestrator(vault_path="./iris_vault", pulse_mode=True)

    # Add all 5 mirrors
    for mirror in create_all_5_mirrors():
        orch.add_mirror(mirror)

    # Load Type 3 (Speculation) prompts
    with open('prompts/type3_speculation_paradigm_s1.txt', 'r') as f:
        type3_s1 = f.read()
    with open('prompts/type3_speculation_paradigm_s2.txt', 'r') as f:
        type3_s2 = f.read()
    with open('prompts/type3_speculation_paradigm_s3.txt', 'r') as f:
        type3_s3 = f.read()
    with open('prompts/type3_speculation_paradigm_s4.txt', 'r') as f:
        type3_s4 = f.read()

    # Temporarily override CHAMBERS
    original_chambers = CHAMBERS.copy()
    CHAMBERS['S1'] = type3_s1
    CHAMBERS['S2'] = type3_s2
    CHAMBERS['S3'] = type3_s3
    CHAMBERS['S4'] = type3_s4

    # Run standard S1-S4 cycle (6 full cycles + 2 synthesis = 26 turns)
    chamber_sequence = ['S1', 'S2', 'S3', 'S4'] * 6 + ['S3', 'S4']

    print("🚀 Starting RUN 6 execution...")
    print(f"   Chambers: {len(chamber_sequence)} turns")
    print(f"   Models: 5 mirrors in parallel PULSE mode")
    print()

    results = orch.run_session(chambers=chamber_sequence)

    # Restore original chambers
    CHAMBERS.update(original_chambers)

    # Summary
    elapsed = time.time() - start_time
    print()
    print("=" * 80)
    print("✅ RUN 6 COMPLETE")
    print("=" * 80)
    print(f"Duration: {elapsed/60:.1f} minutes")
    print(f"Session saved: {results['session_file']}")
    print()
    print("NEXT STEP: Run topology analysis to validate Type 3 predictions")
    print("  Expected: wide width, late/no stabilization, low confidence or non-convergence")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
