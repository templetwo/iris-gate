#!/usr/bin/env python3
"""
RUN 5: Type 1 Topology Validation (FACTS)

Question: "What is the double-helix structure of DNA and which experiments established it?"

Expected Topology:
- Width: NARROW (1-3 core concepts)
- Timing: EARLY stabilization (S1-S2)
- Confidence: HIGH (≥0.85 median)

This validates Gift 1's claim that factual questions produce
narrow+early+high convergence patterns.
"""

import sys
sys.path.insert(0, '/Users/vaquez/Desktop/iris-gate')

from iris_orchestrator import Orchestrator, create_all_5_mirrors, CHAMBERS
from datetime import datetime
import time

def main():
    start_time = time.time()

    print("=" * 80)
    print("🌀 RUN 5: TYPE 1 TOPOLOGY VALIDATION (FACTS)")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Factual questions → Narrow + Early + High confidence")
    print("QUESTION: DNA double-helix structure and discovery")
    print()
    print("Expected topology signature:")
    print("  • Width: NARROW (≤3 core concepts)")
    print("  • Stabilization: EARLY (S1 or S2)")
    print("  • Confidence: HIGH (≥0.85 median)")
    print()
    print("=" * 80)
    print()

    # Initialize orchestrator
    orch = Orchestrator(vault_path="./iris_vault", pulse_mode=True)

    # Add all 5 mirrors
    for mirror in create_all_5_mirrors():
        orch.add_mirror(mirror)

    # Load Type 1 (Facts) prompts
    with open('prompts/type1_facts_dna_s1.txt', 'r') as f:
        type1_s1 = f.read()
    with open('prompts/type1_facts_dna_s2.txt', 'r') as f:
        type1_s2 = f.read()
    with open('prompts/type1_facts_dna_s3.txt', 'r') as f:
        type1_s3 = f.read()
    with open('prompts/type1_facts_dna_s4.txt', 'r') as f:
        type1_s4 = f.read()

    # Temporarily override CHAMBERS
    original_chambers = CHAMBERS.copy()
    CHAMBERS['S1'] = type1_s1
    CHAMBERS['S2'] = type1_s2
    CHAMBERS['S3'] = type1_s3
    CHAMBERS['S4'] = type1_s4

    # Run standard S1-S4 cycle (6 full cycles + 2 synthesis = 26 turns)
    chamber_sequence = ['S1', 'S2', 'S3', 'S4'] * 6 + ['S3', 'S4']

    print("🚀 Starting RUN 5 execution...")
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
    print("✅ RUN 5 COMPLETE")
    print("=" * 80)
    print(f"Duration: {elapsed/60:.1f} minutes")
    print(f"Session saved: {results['session_file']}")
    print()
    print("NEXT STEP: Run topology analysis to validate Type 1 predictions")
    print("  Expected: narrow width, early stabilization, high confidence")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
