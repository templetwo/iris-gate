#!/usr/bin/env python3
"""
RUN 7: TYPE 0 Topology Validation (CRISIS/CONDITIONAL)

Question: "What emergency molecular protocols activate during acute mitochondrial dysfunction?"

Expected Topology:
- Width: NARROW (≤12 core mechanisms)
- Timing: EARLY stabilization (S2-S3 when triggers specified)
- Confidence: CONDITIONAL (spikes when triggers present)
- Trigger dependency: YES (IF-THEN rules)

This validates the 3% hypothesis and completes the epistemic map:
TYPE 0 (Crisis) + TYPE 1 (Facts) + TYPE 2 (Exploration) + TYPE 3 (Speculation)
"""

import sys
sys.path.insert(0, '/Users/vaquez/Desktop/iris-gate')

from iris_orchestrator import Orchestrator, create_all_5_mirrors, CHAMBERS
from datetime import datetime
import time

def main():
    start_time = time.time()

    print("=" * 80)
    print("🌀 RUN 7: TYPE 0 TOPOLOGY VALIDATION (CRISIS/CONDITIONAL)")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Crisis questions → Narrow + Trigger-locked + Conditional confidence")
    print("QUESTION: Emergency protocols in acute mitochondrial dysfunction")
    print()
    print("Expected topology signature:")
    print("  • Width: NARROW (≤12 mechanisms)")
    print("  • Stabilization: EARLY (S2-S3 when triggers specified)")
    print("  • Confidence: CONDITIONAL (higher with triggers)")
    print("  • Decision rules: IF-THEN clauses linking trigger → outcome")
    print()
    print("This tests the 3% hypothesis: invisible until crisis")
    print()
    print("=" * 80)
    print()

    # Initialize orchestrator
    orch = Orchestrator(vault_path="./iris_vault", pulse_mode=True)

    # Add all 5 mirrors
    for mirror in create_all_5_mirrors():
        orch.add_mirror(mirror)

    # Load Type 0 (Crisis) prompts
    with open('prompts/type0_crisis_mitochondria_s1.txt', 'r') as f:
        type0_s1 = f.read()
    with open('prompts/type0_crisis_mitochondria_s2.txt', 'r') as f:
        type0_s2 = f.read()
    with open('prompts/type0_crisis_mitochondria_s3.txt', 'r') as f:
        type0_s3 = f.read()
    with open('prompts/type0_crisis_mitochondria_s4.txt', 'r') as f:
        type0_s4 = f.read()

    # Temporarily override CHAMBERS
    original_chambers = CHAMBERS.copy()
    CHAMBERS['S1'] = type0_s1
    CHAMBERS['S2'] = type0_s2
    CHAMBERS['S3'] = type0_s3
    CHAMBERS['S4'] = type0_s4

    # Run standard S1-S4 cycle (6 full cycles + 2 synthesis = 26 turns)
    chamber_sequence = ['S1', 'S2', 'S3', 'S4'] * 6 + ['S3', 'S4']

    print("🚀 Starting RUN 7 execution...")
    print(f"   Chambers: {len(chamber_sequence)} turns")
    print(f"   Models: 5 mirrors in parallel PULSE mode")
    print()
    print("⚠️  CRISIS MODE: Expecting narrow, trigger-bound convergence")
    print()

    results = orch.run_session(chambers=chamber_sequence)

    # Restore original chambers
    CHAMBERS.update(original_chambers)

    # Summary
    elapsed = time.time() - start_time
    print()
    print("=" * 80)
    print("✅ RUN 7 COMPLETE")
    print("=" * 80)
    print(f"Duration: {elapsed/60:.1f} minutes")
    print(f"Session saved to iris_vault/")
    print()
    print("NEXT STEP: Extract Crisis Protocol Map and validate TYPE 0 predictions")
    print("  Expected: narrow mechanisms, conditional confidence, IF-THEN rules")
    print()
    print("If TYPE 0 validated → Epistemic map complete (TYPE 0, 1, 2, 3)")
    print("If not → Non-convergence report with proposed experiments")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
