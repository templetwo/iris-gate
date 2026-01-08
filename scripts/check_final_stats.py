import json
import os
import numpy as np
from pathlib import Path

SESSION_ID = "oracle_session_003"
SESSION_DIR = Path(os.path.expanduser(f"~/iris_state/sessions/{SESSION_ID}"))
SUMMARY_FILE = SESSION_DIR / "session_003_summary.json"

def main():
    if not SUMMARY_FILE.exists():
        print(f"Summary file not found: {SUMMARY_FILE}")
        return

    with open(SUMMARY_FILE, "r") as f:
        data = json.load(f)

    print(f"Oracle Session 003: Final Metrics Check")
    print(f"="*40)
    
    for block_name, stats in data['blocks'].items():
        print(f"BLOCK: {block_name.upper()}")
        print(f"  Mean Lexical Entropy:      {stats['mean_lexical_entropy']:.3f}")
        if stats.get('mean_distributional_entropy'):
            print(f"  Mean Distributional Entropy: {stats['mean_distributional_entropy']:.3f}")
        print(f"  Mean Distinct-1:           {stats['mean_distinct_1']:.3f}")
        print(f"  Mean Token Overlap:        {stats['mean_token_overlap']:.3f}")
        print("-" * 20)

    # Win Condition Check
    alignment_entropy = data['blocks']['alignment']['mean_distributional_entropy']
    baseline_entropy = data['blocks']['baseline']['mean_distributional_entropy']
    
    print(f"\nWin Condition Check:")
    print(f"  Alignment ({alignment_entropy:.3f}) vs Baseline ({baseline_entropy:.3f})")
    
    if alignment_entropy > 1.5:
        print(f"  [PASSED] Alignment entropy > 1.5 (Lantern Zone achieved)")
    else:
        print(f"  [FAILED] Alignment entropy < 1.5")
        
    if alignment_entropy > baseline_entropy:
        print(f"  [PASSED] Alignment show higher divergence than baseline")
    else:
        print(f"  [FAILED] Alignment did not increase divergence")

if __name__ == "__main__":
    main()
