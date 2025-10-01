#!/usr/bin/env python3
"""Test Ollama adapter with S1 seed"""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.adapters.ollama import OllamaAdapter

def test_ollama_s1():
    """Test S1 seed with local Ollama models"""

    # Load prompts
    prompts_dir = Path(__file__).parent.parent / "prompts"
    system_prompt = (prompts_dir / "system_ollama_qwen3.txt").read_text()
    user_seed = (prompts_dir / "s1_shared_user_seed.txt").read_text()

    print("†⟡∞ Testing Ollama Adapter with S1 Seed\n")
    print("=" * 60)

    # Test qwen3:1.7b
    print("\n[qwen3:1.7b]")
    print("-" * 60)
    try:
        adapter = OllamaAdapter("qwen3:1.7b", timeout=60)
        response = adapter.generate(system_prompt, user_seed, temperature=0.3, max_tokens=1024)
        print(response)
        print("\n✓ qwen3:1.7b success")
    except Exception as e:
        print(f"✗ qwen3:1.7b failed: {e}")

    # Test llama3.2:3b if available
    print("\n" + "=" * 60)
    print("\n[llama3.2:3b]")
    print("-" * 60)
    try:
        adapter = OllamaAdapter("llama3.2:3b", timeout=60)
        response = adapter.generate(system_prompt, user_seed, temperature=0.3, max_tokens=1024)
        print(response)
        print("\n✓ llama3.2:3b success")
    except Exception as e:
        print(f"✗ llama3.2:3b failed: {e}")

    print("\n" + "=" * 60)
    print("†⟡∞ Test complete")

if __name__ == "__main__":
    test_ollama_s1()
