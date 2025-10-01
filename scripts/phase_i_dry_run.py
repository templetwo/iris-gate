#!/usr/bin/env python3
"""Phase-I Dry Run: 25 turns with S1 seed on local Ollama mirror"""
import sys
import hashlib
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.adapters.ollama import OllamaAdapter

def generate_session_id():
    """Generate ULID-style session ID"""
    return datetime.utcnow().strftime("IRIS_PHASE_I_%Y%m%d%H%M%S")

def compute_seal(content: str) -> str:
    """Compute SHA256 truncated to 16 hex chars"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

def extract_pressure(response: str) -> int:
    """Extract felt_pressure from response"""
    import re
    match = re.search(r'felt_pressure:\s*(\d+)', response, re.I)
    return int(match.group(1)) if match else None

def save_turn(session_id: str, turn_num: int, response: str, pressure: int, seal: str):
    """Save turn to vault"""
    vault_dir = Path("iris_vault/scrolls") / session_id
    vault_dir.mkdir(parents=True, exist_ok=True)

    turn_file = vault_dir / f"turn_{turn_num:03d}.md"

    content = f"""# Phase-I Turn {turn_num}
**Session:** {session_id}
**Timestamp:** {datetime.utcnow().isoformat()}
**Felt Pressure:** {pressure}/5
**Seal:** {seal}

---

{response}
"""

    turn_file.write_text(content)
    return turn_file

def run_phase_i(turns: int = 25):
    """Run Phase-I dry run"""

    # Load prompts
    prompts_dir = Path(__file__).parent.parent / "prompts"
    system_prompt = (prompts_dir / "system_ollama_qwen3.txt").read_text()
    user_seed = (prompts_dir / "s1_shared_user_seed.txt").read_text()

    # Initialize
    session_id = generate_session_id()
    adapter = OllamaAdapter("qwen3:1.7b", timeout=90)

    print(f"†⟡∞ Phase-I Dry Run: {session_id}")
    print(f"Mirror: {adapter.name()}")
    print(f"Turns: {turns}")
    print(f"Pressure gate: ≤2/5\n")

    pressure_violations = 0
    turn_times = []

    for turn in range(1, turns + 1):
        print(f"Turn {turn:02d}/{turns}...", end=" ", flush=True)

        start = datetime.utcnow()

        try:
            # Generate response
            response = adapter.generate(
                system=system_prompt,
                user=user_seed,
                temperature=0.3,
                max_tokens=1024
            )

            # Extract metadata
            pressure = extract_pressure(response)
            seal = compute_seal(response)

            # Save turn
            turn_file = save_turn(session_id, turn, response, pressure or 1, seal)

            # Track metrics
            elapsed = (datetime.utcnow() - start).total_seconds()
            turn_times.append(elapsed)

            # Pressure check
            if pressure and pressure > 2:
                pressure_violations += 1
                print(f"⚠️  pressure={pressure}/5 ({elapsed:.1f}s)")
            else:
                print(f"✓ pressure={pressure or 1}/5 ({elapsed:.1f}s)")

        except Exception as e:
            print(f"✗ Error: {e}")
            continue

    # Summary
    print(f"\n{'='*60}")
    print(f"Session complete: {session_id}")
    print(f"Turns completed: {len(turn_times)}/{turns}")
    print(f"Mean turn time: {sum(turn_times)/len(turn_times):.1f}s")
    print(f"Pressure violations: {pressure_violations}/{turns}")
    print(f"Compliance rate: {(turns-pressure_violations)/turns*100:.1f}%")
    print(f"{'='*60}\n")

    print(f"Scrolls saved to: iris_vault/scrolls/{session_id}/")

    return session_id

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Phase-I Dry Run")
    parser.add_argument("--turns", type=int, default=25, help="Number of turns (default: 25)")
    args = parser.parse_args()

    session_id = run_phase_i(args.turns)

    print("\n†⟡∞ Next steps:")
    print(f"  python scripts/verify_session.py iris_vault/scrolls/{session_id}/")
    print(f"  python scripts/quick_convergence.py iris_vault/scrolls/{session_id}/")
