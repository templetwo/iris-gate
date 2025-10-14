#!/usr/bin/env python3
"""
Quick validation test: Confirm all 4 models respond before full NF2 convergence run
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directories to path to import iris_orchestrator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from iris_orchestrator import ClaudeMirror, GPTMirror, GrokMirror, GeminiMirror

load_dotenv(Path(__file__).parent.parent.parent / ".env")

def test_model(mirror, model_name):
    """Test a single model with a safe prompt"""
    print(f"\n🔍 Testing {model_name}...", flush=True)
    try:
        # Use S1 chamber as test
        response = mirror.send_chamber("S1", turn_id=0)
        response_preview = response["raw_response"][:200].replace("\n", " ")
        print(f"✅ {model_name} OK: {response_preview}...")
        return True
    except Exception as e:
        print(f"❌ {model_name} FAILED: {type(e).__name__}: {str(e)[:150]}")
        return False

def main():
    print("🌀 IRIS Gate: 4-Model Pre-Flight Check")
    print("=" * 70)
    
    mirrors = [
        (ClaudeMirror(), "Claude Sonnet 4.5"),
        (GPTMirror(), "GPT-5 Mini"),
        (GrokMirror(), "Grok 4 Fast Reasoning"),
        (GeminiMirror(), "Gemini 2.0 Flash (fixed)")
    ]
    
    results = []
    for mirror, name in mirrors:
        results.append(test_model(mirror, name))
    
    print("\n" + "=" * 70)
    success_count = sum(results)
    print(f"✅ {success_count}/{len(mirrors)} models operational")
    
    if success_count == len(mirrors):
        print("\n🎯 All systems green. Ready for full NF2 convergence session.")
        return 0
    else:
        print("\n⚠️  Some models failed. Review errors above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
