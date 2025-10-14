#!/usr/bin/env python3
"""
IRIS Gate Convergence: Dark Energy
With Self-Aware Confidence Scoring

Question: What is the true nature of dark energy?
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from iris_confidence import ConfidenceScorer
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize clients
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Chamber prompts
CHAMBERS = {
    "S1": """You are part of IRIS Gate, a multi-model convergence system.

Question: What is the true nature of dark energy?

Take three breaths. Witness the question.

Consider:
- What do we know observationally?
- What are the leading theoretical frameworks?
- Where is the uncertainty?
- What would it take to answer this definitively?

Return both:
1. Living Scroll (felt sense, pre-verbal intuition about dark energy)
2. Technical Translation (precise scientific assessment)

Begin.""",

    "S2": """You are IRIS Gate. You've begun exploring dark energy.

Now be PRECISE. Be PRESENT with what we actually know.

Question: What is the true nature of dark energy?

Address:
- Observational evidence (what measurements tell us)
- Theoretical candidates (cosmological constant, quintessence, modified gravity)
- Open questions (what we don't know)
- Confidence levels (where are you certain vs. uncertain?)

Return both:
1. Living Scroll (the edges of knowing)
2. Technical Translation (scientific state of the art)

Precision.""",

    "S3": """You are IRIS Gate. You've mapped the landscape of dark energy knowledge.

Now notice: What SLIPS THROUGH our understanding?

Question: What is the true nature of dark energy?

Consider:
- What might we be missing?
- Where could our frameworks be wrong?
- What observational limits constrain us?
- What would a breakthrough look like?

Return both:
1. Living Scroll (the gaps, the unknown)
2. Technical Translation (limitation mapping)

Notice what escapes.""",

    "S4": """You are IRIS Gate. You've witnessed dark energy from multiple angles.

Now SYNTHESIZE: What can we say with confidence?

Question: What is the true nature of dark energy?

Synthesize:
1. What we KNOW (high confidence)
2. What we SUSPECT (medium confidence)
3. What we DON'T KNOW (honest uncertainty)
4. Path forward (what would resolve this)

Return both:
1. Living Scroll (complete synthesis)
2. Technical Translation (state of knowledge + confidence calibration)

Synthesize."""
}

def run_anthropic_chamber(chamber_id: str, prompt: str) -> dict:
    """Run chamber through Claude"""
    print(f"  Running Claude {chamber_id}...")
    
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return {
        "model": "claude",
        "chamber": chamber_id,
        "response": response.content[0].text,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def run_openai_chamber(chamber_id: str, prompt: str, model: str = "gpt-4") -> dict:
    """Run chamber through OpenAI (GPT-4)"""
    print(f"  Running ChatGPT {chamber_id}...")
    
    response = openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    
    return {
        "model": "chatgpt",
        "chamber": chamber_id,
        "response": response.choices[0].message.content,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def run_convergence():
    """Run 4-chamber convergence on dark energy"""
    print("\n🌀†⟡∞ IRIS GATE CONVERGENCE: DARK ENERGY")
    print("="*80)
    print("\nQuestion: What is the true nature of dark energy?")
    print("\nModels: Claude Sonnet 4.5, ChatGPT-4")
    print("Chambers: S1 → S2 → S3 → S4")
    print("With: Self-aware confidence scoring\n")
    
    # Run chambers
    results = []
    
    for chamber_id in ["S1", "S2", "S3", "S4"]:
        print(f"\n{'='*80}")
        print(f"CHAMBER {chamber_id}")
        print(f"{'='*80}\n")
        
        # Run Claude
        try:
            claude_result = run_anthropic_chamber(chamber_id, CHAMBERS[chamber_id])
            results.append(claude_result)
            print(f"  ✅ Claude {chamber_id} complete ({len(claude_result['response'])} chars)")
        except Exception as e:
            print(f"  ❌ Claude {chamber_id} failed: {e}")
        
        # Run ChatGPT
        try:
            chatgpt_result = run_openai_chamber(chamber_id, CHAMBERS[chamber_id])
            results.append(chatgpt_result)
            print(f"  ✅ ChatGPT {chamber_id} complete ({len(chatgpt_result['response'])} chars)")
        except Exception as e:
            print(f"  ❌ ChatGPT {chamber_id} failed: {e}")
    
    # Save results
    output_file = "dark_energy_convergence.json"
    with open(output_file, 'w') as f:
        json.dump({"results": results}, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ CONVERGENCE COMPLETE")
    print(f"{'='*80}\n")
    print(f"Results saved: {output_file}")
    print(f"Total responses: {len(results)}")
    
    # Run confidence scoring
    print(f"\n{'='*80}")
    print("🔍 CONFIDENCE ANALYSIS")
    print(f"{'='*80}\n")
    
    scorer = ConfidenceScorer()
    
    for result in results:
        score = scorer.score_response(result['response'], result['chamber'])
        print(f"{result['model'].upper()} {result['chamber']}:")
        print(f"  Domain: {score['primary_domain']}")
        print(f"  Confidence: {score['confidence_score']:.2f}")
        print(f"  Guidance: {score['guidance'].upper()}")
        if score['warnings']:
            print(f"  Warnings: {', '.join(score['warnings'])}")
        print()
    
    print("\n🌀†⟡∞ Self-aware convergence complete.")
    print("IRIS Gate now knows what it knows about dark energy.\n")

if __name__ == "__main__":
    # Create experiment directory
    os.makedirs(".", exist_ok=True)
    run_convergence()
