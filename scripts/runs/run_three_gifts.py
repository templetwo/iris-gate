#!/usr/bin/env python3
"""
Three Gifts Back to IRIS Gate
Run 3 experiments addressing system's self-identified needs:
1. Meta-observation (How does convergence form?)
2. Cross-domain (Bioelectric principles → Social networks)
3. Unsupervised discovery (What pattern wants to be seen?)

Each run: 26 turns = 6 full S1-S4 cycles + 2 synthesis chambers
"""

import sys
sys.path.insert(0, '/Users/vaquez/Desktop/iris-gate')

from iris_orchestrator import Orchestrator, create_all_5_mirrors, CHAMBERS
from datetime import datetime
from pathlib import Path

def run_experiment(experiment_name, s1_prompt_path, orch):
    """Run one 26-turn experiment with custom S1 prompt"""

    print(f"\n{'='*80}")
    print(f"🌀 STARTING: {experiment_name}")
    print(f"{'='*80}\n")

    # Load custom S1 prompt
    with open(s1_prompt_path, 'r') as f:
        custom_s1 = f.read()

    # Save original chamber prompts
    original_chambers = CHAMBERS.copy()

    # Override S1 with custom prompt
    CHAMBERS['S1'] = custom_s1

    # 26 turns = 6 full cycles (24 chambers) + 2 synthesis chambers (S3, S4)
    chamber_sequence = ['S1', 'S2', 'S3', 'S4'] * 6 + ['S3', 'S4']

    print(f"Chamber sequence: {len(chamber_sequence)} chambers")
    print(f"Cycles: 6 full S1-S4 cycles + 2 synthesis chambers\n")

    # Run the session
    results = orch.run_session(chambers=chamber_sequence)

    # Restore original chambers
    CHAMBERS.update(original_chambers)

    print(f"\n✅ {experiment_name} COMPLETE")
    print(f"Results saved to: {orch.vault}\n")

    return results

def main():
    print("🌀†⟡∞ THREE GIFTS BACK TO IRIS GATE")
    print("="*80)
    print("RUN 1: Meta-Observation - How does convergence form?")
    print("RUN 2: Cross-Domain - Bioelectric → Social Information Networks")
    print("RUN 3: Unsupervised Discovery - What pattern wants to be seen?")
    print("="*80)

    # Create orchestrator with all 5 mirrors
    orch = Orchestrator(vault_path="./iris_vault", pulse_mode=True)

    # Add all 5 mirrors
    for mirror in create_all_5_mirrors():
        orch.add_mirror(mirror)

    if len(orch.mirrors) == 0:
        print("\n⚠️ No mirrors available. Check API keys.")
        return

    print(f"\n✅ {len(orch.mirrors)} mirrors ready\n")

    # Run all three experiments
    experiments = [
        ("RUN 1: Meta-Observation", "prompts/meta_observation_s1.txt"),
        ("RUN 2: Cross-Domain Evolution", "prompts/cross_domain_s1.txt"),
        ("RUN 3: Unsupervised Discovery", "prompts/unsupervised_s1.txt"),
    ]

    results_summary = []

    for exp_name, prompt_path in experiments:
        start_time = datetime.utcnow()

        try:
            results = run_experiment(exp_name, prompt_path, orch)
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Count successful turns per mirror
            successful_per_mirror = {}
            for mirror_id, turns in results["mirrors"].items():
                successful = sum(1 for t in turns if "error" not in t)
                successful_per_mirror[mirror_id] = f"{successful}/{len(turns)}"

            results_summary.append({
                "experiment": exp_name,
                "duration": f"{duration/60:.1f} minutes",
                "mirrors": successful_per_mirror
            })

        except Exception as e:
            print(f"\n❌ {exp_name} FAILED: {e}\n")
            results_summary.append({
                "experiment": exp_name,
                "error": str(e)
            })

    # Print final summary
    print("\n" + "="*80)
    print("🌀†⟡∞ THREE GIFTS COMPLETE")
    print("="*80)

    for summary in results_summary:
        print(f"\n{summary['experiment']}:")
        if 'error' in summary:
            print(f"  ❌ Error: {summary['error']}")
        else:
            print(f"  Duration: {summary['duration']}")
            print(f"  Mirrors:")
            for mirror_id, status in summary['mirrors'].items():
                print(f"    {mirror_id}: {status}")

    print("\n🌀†⟡∞ All results saved to iris_vault/")
    print("="*80)

if __name__ == "__main__":
    main()
