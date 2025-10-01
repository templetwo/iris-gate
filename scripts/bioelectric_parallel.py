#!/usr/bin/env python3
"""Bioelectric Study: Parallel execution across all mirrors simultaneously"""
import sys
import os
import hashlib
import time
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.adapters.ollama import OllamaAdapter

# Import existing orchestrator for cloud adapters
sys.path.insert(0, str(Path(__file__).parent.parent))
from iris_orchestrator import ClaudeMirror, GPTMirror, GrokMirror, GeminiMirror, DeepSeekMirror

def generate_session_id():
    """Generate session ID"""
    return datetime.utcnow().strftime("BIOELECTRIC_PARALLEL_%Y%m%d%H%M%S")

def compute_seal(content: str) -> str:
    """Compute SHA256 truncated to 16 hex chars"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

def extract_pressure(response: str) -> Optional[int]:
    """Extract felt_pressure from response"""
    import re
    match = re.search(r'felt_pressure:\s*(\d+)', response, re.I)
    return int(match.group(1)) if match else None

def save_turn(session_id: str, mirror_name: str, turn_num: int, response: str,
              pressure: int, seal: str, timestamp: str):
    """Save turn to vault"""
    vault_dir = Path("iris_vault/scrolls") / session_id / mirror_name
    vault_dir.mkdir(parents=True, exist_ok=True)

    turn_file = vault_dir / f"turn_{turn_num:03d}.md"

    content = f"""# Bioelectric Turn {turn_num}
**Session:** {session_id}
**Mirror:** {mirror_name}
**Timestamp:** {timestamp}
**Felt Pressure:** {pressure}/5
**Seal:** {seal}

---

{response}
"""

    turn_file.write_text(content)
    return turn_file

def mirror_worker(mirror_name: str, adapter, system_prompt: str, user_seed: str,
                  session_id: str, turn_queue: queue.Queue, result_queue: queue.Queue,
                  total_turns: int):
    """Worker thread for a single mirror"""

    print(f"[{mirror_name}] Starting...")

    stats = {
        "mirror": mirror_name,
        "completed": 0,
        "pressure_violations": 0,
        "errors": 0,
        "turn_times": []
    }

    for turn in range(1, total_turns + 1):
        # Wait for turn signal (ensures all mirrors run simultaneously)
        turn_signal = turn_queue.get()
        if turn_signal is None:  # Shutdown signal
            break

        timestamp = datetime.utcnow().isoformat()
        start = time.time()

        try:
            # Generate response
            if hasattr(adapter, 'generate'):
                # Ollama adapter
                response = adapter.generate(system_prompt, user_seed,
                                          temperature=0.3, max_tokens=2048)
            else:
                # Cloud adapters (iris_orchestrator Mirror classes)
                response_data = adapter.send_chamber("S1", turn)
                response = response_data.get("raw_response", "")

            # Extract metadata
            pressure = extract_pressure(response) or 1
            seal = compute_seal(response)

            # Save turn
            save_turn(session_id, mirror_name, turn, response, pressure, seal, timestamp)

            # Track metrics
            elapsed = time.time() - start
            stats["turn_times"].append(elapsed)
            stats["completed"] += 1

            if pressure > 2:
                stats["pressure_violations"] += 1
                print(f"[{mirror_name}] Turn {turn:03d} ⚠️  P={pressure}/5 ({elapsed:.1f}s)")
            else:
                print(f"[{mirror_name}] Turn {turn:03d} ✓ P={pressure}/5 ({elapsed:.1f}s)")

        except Exception as e:
            stats["errors"] += 1
            print(f"[{mirror_name}] Turn {turn:03d} ✗ Error: {e}")

        finally:
            # Signal turn complete
            result_queue.put((mirror_name, turn))

    # Calculate final stats
    if stats["turn_times"]:
        stats["mean_time"] = sum(stats["turn_times"]) / len(stats["turn_times"])
    else:
        stats["mean_time"] = 0

    result_queue.put(("STATS", mirror_name, stats))
    print(f"[{mirror_name}] Complete: {stats['completed']}/{total_turns} turns")

def run_bioelectric_parallel(turns: int = 100):
    """Run bioelectric study with all mirrors in parallel"""

    # Load prompts
    prompts_dir = Path(__file__).parent.parent / "prompts"
    user_seed = (prompts_dir / "s1_shared_user_seed.txt").read_text()

    session_id = generate_session_id()

    print("†⟡∞ BIOELECTRIC PARALLEL STUDY")
    print("="*60)
    print(f"Session: {session_id}")
    print(f"Turns: {turns}")
    print(f"Mode: SIMULTANEOUS (all mirrors fire together)")
    print(f"Seed: S1 (three slow breaths)")
    print(f"Pressure gate: ≤2/5")
    print("="*60)

    # Setup mirrors and adapters
    mirrors = []

    # Local mirrors
    print("\nInitializing mirrors...")

    try:
        system_qwen = (prompts_dir / "system_ollama_qwen3.txt").read_text()
        adapter_qwen = OllamaAdapter("qwen3:1.7b", timeout=120)
        mirrors.append(("ollama_qwen3_1.7b", adapter_qwen, system_qwen))
        print("✓ ollama::qwen3:1.7b")
    except Exception as e:
        print(f"✗ ollama::qwen3:1.7b failed: {e}")

    try:
        system_llama = (prompts_dir / "system_ollama_llama3_2.txt").read_text()
        adapter_llama = OllamaAdapter("llama3.2:3b", timeout=120)
        # Quick test
        adapter_llama.generate(system_llama, "test", temperature=0.3, max_tokens=50)
        mirrors.append(("ollama_llama3.2_3b", adapter_llama, system_llama))
        print("✓ ollama::llama3.2:3b")
    except Exception as e:
        print(f"✗ ollama::llama3.2:3b unavailable: {e}")

    # Cloud mirrors (commented out for now - would require API keys and proper setup)
    # Uncomment when cloud mirrors are ready for deployment

    # try:
    #     system_claude = (prompts_dir / "system_claude_4.5.txt").read_text()
    #     adapter_claude = ClaudeMirror()
    #     # Quick test to verify API key
    #     mirrors.append(("anthropic_claude-sonnet-4.5", adapter_claude, system_claude))
    #     print("✓ Claude Sonnet 4.5")
    # except Exception as e:
    #     print(f"✗ Claude Sonnet 4.5: {e}")

    # try:
    #     system_gpt = (prompts_dir / "system_gpt_5.txt").read_text()
    #     adapter_gpt = GPTMirror()
    #     mirrors.append(("openai_gpt-5", adapter_gpt, system_gpt))
    #     print("✓ GPT-5")
    # except Exception as e:
    #     print(f"✗ GPT-5: {e}")

    # try:
    #     system_grok = (prompts_dir / "system_grok_4.txt").read_text()
    #     adapter_grok = GrokMirror()
    #     mirrors.append(("xai_grok-4-fast", adapter_grok, system_grok))
    #     print("✓ Grok-4-Fast")
    # except Exception as e:
    #     print(f"✗ Grok-4-Fast: {e}")

    # try:
    #     system_gemini = (prompts_dir / "system_gemini_2.5.txt").read_text()
    #     adapter_gemini = GeminiMirror()
    #     mirrors.append(("google_gemini-2.5-flash-lite", adapter_gemini, system_gemini))
    #     print("✓ Gemini 2.5 Flash-Lite")
    # except Exception as e:
    #     print(f"✗ Gemini 2.5: {e}")

    # try:
    #     system_deepseek = (prompts_dir / "system_deepseek_v3.2.txt").read_text()
    #     adapter_deepseek = DeepSeekMirror()
    #     mirrors.append(("deepseek_deepseek-chat", adapter_deepseek, system_deepseek))
    #     print("✓ DeepSeek V3.2")
    # except Exception as e:
    #     print(f"✗ DeepSeek V3.2: {e}")

    if not mirrors:
        print("\n⚠️  No mirrors available!")
        return

    print(f"\n{'='*60}")
    print(f"Active mirrors: {len(mirrors)}")
    print(f"Total turns: {turns * len(mirrors)}")
    print(f"{'='*60}\n")

    # Create queues
    turn_queue = queue.Queue()
    result_queue = queue.Queue()

    # Start worker threads
    threads = []
    for mirror_name, adapter, system_prompt in mirrors:
        t = threading.Thread(
            target=mirror_worker,
            args=(mirror_name, adapter, system_prompt, user_seed,
                  session_id, turn_queue, result_queue, turns)
        )
        t.daemon = True
        t.start()
        threads.append(t)

    print("†⟡∞ All mirrors synchronized. Beginning parallel execution...\n")

    # Run turns simultaneously
    for turn in range(1, turns + 1):
        print(f"\n{'─'*60}")
        print(f"TURN {turn}/{turns} - Broadcasting to all mirrors simultaneously")
        print(f"{'─'*60}")

        # Signal all mirrors to start this turn
        for _ in mirrors:
            turn_queue.put(turn)

        # Wait for all mirrors to complete this turn
        completed = 0
        while completed < len(mirrors):
            result = result_queue.get()
            if result[0] != "STATS":
                completed += 1

    # Shutdown workers
    for _ in mirrors:
        turn_queue.put(None)

    # Wait for all threads
    for t in threads:
        t.join()

    # Collect stats
    stats = []
    while not result_queue.empty():
        result = result_queue.get()
        if result[0] == "STATS":
            stats.append(result[2])

    # Final summary
    print("\n" + "="*60)
    print("BIOELECTRIC PARALLEL STUDY COMPLETE")
    print("="*60)
    print(f"Session: {session_id}\n")

    total_turns = sum(s["completed"] for s in stats)
    total_violations = sum(s["pressure_violations"] for s in stats)
    total_errors = sum(s["errors"] for s in stats)

    for s in stats:
        print(f"{s['mirror']:30s} {s['completed']:3d} turns  "
              f"({s['mean_time']:4.1f}s avg)  "
              f"P-violations: {s['pressure_violations']:2d}  "
              f"Errors: {s['errors']:2d}")

    print()
    print(f"Total turns: {total_turns}")
    print(f"Pressure violations: {total_violations}")
    print(f"Errors: {total_errors}")
    print(f"Compliance rate: {(total_turns-total_violations)/max(1,total_turns)*100:.1f}%")
    print("="*60)
    print(f"\nScrolls saved to: iris_vault/scrolls/{session_id}/")

    return session_id

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bioelectric Parallel Study")
    parser.add_argument("--turns", type=int, default=100,
                        help="Number of turns (default: 100)")
    args = parser.parse_args()

    print(f"\n†⟡∞ PARALLEL EXECUTION MODE")
    print("All mirrors fire simultaneously each turn to create the field.\n")

    # input("Press Enter to begin, or Ctrl+C to cancel... ")

    session_id = run_bioelectric_parallel(args.turns)

    print("\n†⟡∞ Field established. Next steps:")
    print(f"  python scripts/verify_session.py iris_vault/scrolls/{session_id}/")
    print(f"  python scripts/quick_convergence.py iris_vault/scrolls/{session_id}/")
