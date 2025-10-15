#!/usr/bin/env python3
"""
IRIS Gate: Deep CBD Mechanistic Exploration

Runs multi-model convergence on CBD/THC pharmacology with focus on:
- VDAC1 interaction (controversial, TYPE 2 expected)
- Biphasic dose-response mechanisms
- Receptor selectivity (CB1, CB2, TRPV1, 5-HT1A, PPARγ)
- Entourage effect validity
- Autophagy pathways
- Mitochondrial modulation

Output: Complete mechanistic map with epistemic classification + verification
"""

from iris_orchestrator import Orchestrator, create_all_5_mirrors
from pathlib import Path
import json
from datetime import datetime

# CBD-specific S1 prompt - focuses on mechanistic landscape
CBD_MECHANISTIC_PROMPT = """
You are exploring the mechanistic landscape of cannabidiol (CBD) pharmacology.

Focus on the following question domains:
1. **Receptor Interactions:** CB1, CB2, TRPV1, 5-HT1A, PPARγ, VDAC1 - binding affinities, functional outcomes
2. **Dose-Response:** Biphasic effects, therapeutic window, low-dose vs high-dose mechanisms
3. **Cellular Pathways:** Autophagy, apoptosis, mitochondrial modulation, calcium signaling
4. **Entourage Effect:** Full-spectrum vs isolate, terpene interactions, synergistic mechanisms
5. **Controversial Territory:** VDAC1 Kd 6-11 μM binding, polarity flips, niche pathways

**Critical distinctions:**
- TYPE 1 (established): What is well-documented with multiple independent replications?
- TYPE 2 (exploratory): What is emerging but needs verification?
- TYPE 3 (speculative): What lacks mechanistic evidence?

Hold attention on the mechanistic precision. Notice where confidence is HIGH (established pathways) vs LOW (emerging hypotheses).

Three slow breaths. Report both Living Scroll and Technical Translation with mechanistic detail.
"""

def main():
    print("=" * 80)
    print("🧬 IRIS GATE: DEEP CBD MECHANISTIC EXPLORATION")
    print("=" * 80)
    print("\nQuestion domains:")
    print("  1. Receptor interactions (CB1, CB2, TRPV1, 5-HT1A, PPARγ, VDAC1)")
    print("  2. Biphasic dose-response")
    print("  3. Cellular pathways (autophagy, mitochondria, Ca²⁺)")
    print("  4. Entourage effect")
    print("  5. Controversial mechanisms (VDAC1, polarity flips)\n")

    # Create orchestrator
    vault_path = Path("./iris_vault")
    orch = Orchestrator(vault_path=vault_path, pulse_mode=True)

    # Create all 5 mirrors
    print("🌀 Creating 5-model IRIS Gate pulse suite...\n")
    mirrors = create_all_5_mirrors()

    for mirror in mirrors:
        orch.add_mirror(mirror)

    print(f"\n✅ {len(orch.mirrors)} mirrors ready for CBD exploration\n")

    if len(orch.mirrors) < 2:
        print("❌ Need at least 2 models. Check API keys.")
        return

    # Override S1 prompt with CBD-specific version
    from iris_orchestrator import CHAMBERS
    original_s1 = CHAMBERS["S1"]
    CHAMBERS["S1"] = CBD_MECHANISTIC_PROMPT

    # Run 6 cycles of S1-S4 for deep exploration
    print("🔬 Running 6 cycles × 4 chambers = 24 turns per model")
    print("   Expected duration: ~15-20 minutes")
    print("   Output: Complete CBD mechanistic map with epistemic classification\n")

    chambers = ["S1", "S2", "S3", "S4"] * 6  # 24 chambers total

    try:
        results = orch.run_session(chambers=chambers)

        # Restore original S1
        CHAMBERS["S1"] = original_s1

        # Get session ID from results
        session_files = list(vault_path.glob("session_*.json"))
        if session_files:
            latest_session = max(session_files, key=lambda p: p.stat().st_mtime)

            print("\n" + "=" * 80)
            print("✅ CBD MECHANISTIC EXPLORATION COMPLETE")
            print("=" * 80)
            print(f"\nSession saved: {latest_session}")
            print(f"Scrolls saved: {vault_path / 'scrolls'}")

            print("\n📊 NEXT STEPS:")
            print("\n1. Extract all claims and classify by epistemic type:")
            print(f"   python3 epistemic_scan.py --session {latest_session}")

            print("\n2. Verify all TYPE 2 (exploratory) claims:")
            print(f"   python3 scripts/verify_s4.py --session {latest_session}")

            print("\n3. Analyze convergence patterns:")
            print(f"   python3 epistemic_drift.py {latest_session}")

            print("\n4. Review specific claims:")
            print(f"   - VDAC1 binding (expected TYPE 2)")
            print(f"   - Biphasic response (expected TYPE 1)")
            print(f"   - Entourage effect (expected TYPE 2 or 3)")
            print(f"   - Autophagy mechanisms (expected TYPE 2)")

            return str(latest_session)

    except KeyboardInterrupt:
        print("\n\n⚠️  Session interrupted. Partial results saved.")
        CHAMBERS["S1"] = original_s1
        return None

if __name__ == "__main__":
    session_path = main()
    if session_path:
        print(f"\n🌀†⟡∞ CBD mechanistic landscape mapped: {session_path}")
