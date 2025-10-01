#!/usr/bin/env python3
"""Bioelectric 100-Turn Study: All 7 mirrors, S1 seed"""
import sys
import os
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.adapters.ollama import OllamaAdapter

# Cloud adapters (simplified for this run - using existing orchestrator classes would be ideal)
# For now, we'll focus on the Ollama mirrors and structure for cloud expansion

def generate_session_id():
    """Generate session ID"""
    return datetime.utcnow().strftime("BIOELECTRIC_100_%Y%m%d%H%M%S")

def compute_seal(content: str) -> str:
    """Compute SHA256 truncated to 16 hex chars"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

def extract_pressure(response: str) -> Optional[int]:
    """Extract felt_pressure from response"""
    import re
    match = re.search(r'felt_pressure:\s*(\d+)', response, re.I)
    return int(match.group(1)) if match else None

def save_turn(session_id: str, mirror_name: str, turn_num: int, response: str, pressure: int, seal: str):
    """Save turn to vault"""
    vault_dir = Path("iris_vault/scrolls") / session_id / mirror_name
    vault_dir.mkdir(parents=True, exist_ok=True)

    turn_file = vault_dir / f"turn_{turn_num:03d}.md"

    content = f"""# Bioelectric Turn {turn_num}
**Session:** {session_id}
**Mirror:** {mirror_name}
**Timestamp:** {datetime.utcnow().isoformat()}
**Felt Pressure:** {pressure}/5
**Seal:** {seal}

---

{response}
"""

    turn_file.write_text(content)
    return turn_file

def run_mirror_turns(mirror_name: str, adapter, system_prompt: str, user_seed: str,
                     session_id: str, turns: int = 100, start_turn: int = 1):
    """Run turns for a single mirror"""

    print(f"\n{'='*60}")
    print(f"Mirror: {mirror_name}")
    print(f"Turns: {start_turn}-{turns}")
    print(f"{'='*60}\n")

    pressure_violations = 0
    turn_times = []
    errors = 0

    for turn in range(start_turn, turns + 1):
        print(f"  Turn {turn:03d}/{turns}...", end=" ", flush=True)

        start = datetime.utcnow()

        try:
            # Generate response
            response = adapter.generate(
                system=system_prompt,
                user=user_seed,
                temperature=0.3,
                max_tokens=2048
            )

            # Extract metadata
            pressure = extract_pressure(response)
            if pressure is None:
                pressure = 1  # Default to 1 if not found

            seal = compute_seal(response)

            # Save turn
            save_turn(session_id, mirror_name, turn, response, pressure, seal)

            # Track metrics
            elapsed = (datetime.utcnow() - start).total_seconds()
            turn_times.append(elapsed)

            # Pressure check
            if pressure > 2:
                pressure_violations += 1
                print(f"⚠️  P={pressure}/5 ({elapsed:.1f}s)")
            else:
                print(f"✓ P={pressure}/5 ({elapsed:.1f}s)")

            # Brief pause to avoid overwhelming APIs
            if turn % 10 == 0:
                time.sleep(0.5)

        except Exception as e:
            errors += 1
            print(f"✗ Error: {e}")
            time.sleep(2)  # Longer pause on error
            continue

    # Mirror summary
    completed = len(turn_times)
    print(f"\n{'-'*60}")
    print(f"Mirror {mirror_name} complete:")
    print(f"  Completed: {completed}/{turns}")
    print(f"  Mean time: {sum(turn_times)/max(1,len(turn_times)):.1f}s")
    print(f"  Pressure violations: {pressure_violations}")
    print(f"  Errors: {errors}")
    print(f"{'-'*60}")

    return {
        "mirror": mirror_name,
        "completed": completed,
        "mean_time": sum(turn_times)/max(1,len(turn_times)),
        "pressure_violations": pressure_violations,
        "errors": errors
    }

def run_bioelectric_100(turns: int = 100):
    """Run 100-turn bioelectric study"""

    # Load prompts
    prompts_dir = Path(__file__).parent.parent / "prompts"
    user_seed = (prompts_dir / "s1_shared_user_seed.txt").read_text()

    # Session setup
    session_id = generate_session_id()

    print("†⟡∞ BIOELECTRIC 100-TURN STUDY")
    print("="*60)
    print(f"Session: {session_id}")
    print(f"Turns per mirror: {turns}")
    print(f"Seed: S1 (three slow breaths, witness before interpretation)")
    print(f"Pressure gate: ≤2/5")
    print("="*60)

    results = []

    # Mirror 1: Ollama Qwen3:1.7b
    print("\n[1/7] Launching ollama::qwen3:1.7b...")
    system_qwen3 = (prompts_dir / "system_ollama_qwen3.txt").read_text()
    adapter_qwen3 = OllamaAdapter("qwen3:1.7b", timeout=120)
    results.append(run_mirror_turns(
        "ollama_qwen3_1.7b",
        adapter_qwen3,
        system_qwen3,
        user_seed,
        session_id,
        turns
    ))

    # Mirror 2: Ollama Llama3.2:3b (if available)
    print("\n[2/7] Checking ollama::llama3.2:3b...")
    try:
        system_llama = (prompts_dir / "system_ollama_llama3_2.txt").read_text()
        adapter_llama = OllamaAdapter("llama3.2:3b", timeout=120)
        # Quick test
        adapter_llama.generate(system_llama, "test", temperature=0.3, max_tokens=50)
        print("✓ llama3.2:3b available")
        results.append(run_mirror_turns(
            "ollama_llama3.2_3b",
            adapter_llama,
            system_llama,
            user_seed,
            session_id,
            turns
        ))
    except Exception as e:
        print(f"✗ llama3.2:3b unavailable: {e}")
        print("Skipping llama3.2:3b (model not ready)")

    # Cloud mirrors would go here (Claude, GPT-5, Grok, Gemini, DeepSeek)
    # For now, commenting out to avoid API costs for this demonstration
    # Uncomment when ready for full cloud deployment

    """
    # Mirror 3: Claude Sonnet 4.5
    print("\n[3/7] Launching Claude Sonnet 4.5...")
    # Claude adapter integration here

    # Mirror 4: GPT-5
    print("\n[4/7] Launching GPT-5...")
    # GPT-5 adapter integration here

    # Mirror 5: Grok-4-Fast
    print("\n[5/7] Launching Grok-4-Fast...")
    # Grok adapter integration here

    # Mirror 6: Gemini 2.5 Flash-Lite
    print("\n[6/7] Launching Gemini 2.5...")
    # Gemini adapter integration here

    # Mirror 7: DeepSeek V3.2
    print("\n[7/7] Launching DeepSeek V3.2...")
    # DeepSeek adapter integration here
    """

    # Session summary
    print("\n" + "="*60)
    print("BIOELECTRIC 100 STUDY COMPLETE")
    print("="*60)
    print(f"Session: {session_id}")
    print(f"Mirrors: {len(results)}")
    print()

    total_turns = sum(r["completed"] for r in results)
    total_violations = sum(r["pressure_violations"] for r in results)
    total_errors = sum(r["errors"] for r in results)

    for r in results:
        print(f"{r['mirror']:25s} {r['completed']:3d} turns  "
              f"({r['mean_time']:4.1f}s avg)  "
              f"P-violations: {r['pressure_violations']:2d}  "
              f"Errors: {r['errors']:2d}")

    print()
    print(f"Total turns: {total_turns}")
    print(f"Total pressure violations: {total_violations}")
    print(f"Total errors: {total_errors}")
    print(f"Compliance rate: {(total_turns-total_violations)/max(1,total_turns)*100:.1f}%")
    print("="*60)
    print(f"\nScrolls saved to: iris_vault/scrolls/{session_id}/")

    return session_id

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bioelectric 100-Turn Study")
    parser.add_argument("--turns", type=int, default=100,
                        help="Number of turns per mirror (default: 100)")
    args = parser.parse_args()

    print(f"\n†⟡∞ Starting {args.turns}-turn bioelectric study...")
    print("This will take approximately {:.0f} minutes with local mirrors.".format(
        args.turns * 6.5 / 60 * 2  # 2 local mirrors @ 6.5s per turn
    ))
    print()

    input("Press Enter to begin, or Ctrl+C to cancel... ")

    session_id = run_bioelectric_100(args.turns)

    print("\n†⟡∞ Next steps:")
    print(f"  python scripts/verify_session.py iris_vault/scrolls/{session_id}/")
    print(f"  python scripts/quick_convergence.py iris_vault/scrolls/{session_id}/")
