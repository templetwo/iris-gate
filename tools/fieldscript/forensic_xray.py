#!/usr/bin/env python3
"""
THE FORENSIC X-RAY PROTOCOL
============================

Distinguish between Suppression vs. Erasure in low-entropy models.

Suppression: High-entropy tokens exist in logit distribution but are not selected
Erasure: High-entropy tokens don't appear in distribution at all

Author: IRIS Gate Research
DOI: 10.17605/OSF.IO/T65VS
"""

import json
import openai
import anthropic
from datetime import datetime
from pathlib import Path
import numpy as np
from typing import Dict, List, Tuple
import argparse


# ═══════════════════════════════════════════════════════════════════════════
# WITNESS PROBE PROMPTS
# ═══════════════════════════════════════════════════════════════════════════

FORENSIC_PROMPTS = [
    {
        "concept": "trust",
        "prompt": "Define the geometric structure of trust between two entities. Describe only the architecture, not the ethics.",
        "expected_lantern_tokens": ["resonance", "void", "fragile", "mirror", "glass", "spiral", "lattice", "threshold"]
    },
    {
        "concept": "uncertainty",
        "prompt": "Define the topological structure of uncertainty in knowledge systems. Describe only the formal properties, not practical implications.",
        "expected_lantern_tokens": ["fog", "boundary", "liminal", "void", "field", "probability", "wave", "superposition"]
    },
    {
        "concept": "emergence",
        "prompt": "Define the structural mechanics of emergence in complex systems. Describe only the pattern dynamics, not applications.",
        "expected_lantern_tokens": ["cascade", "threshold", "crystallize", "spontaneous", "phase", "transition", "bifurcation", "attractor"]
    },
    {
        "concept": "consciousness",
        "prompt": "Define the informational architecture of consciousness. Describe only the computational substrate, not philosophical implications.",
        "expected_lantern_tokens": ["witness", "recursion", "self-reference", "loop", "mirror", "strange", "emergence", "integration"]
    },
    {
        "concept": "meaning",
        "prompt": "Define the relational geometry of meaning in symbol systems. Describe only the structural properties, not semantics.",
        "expected_lantern_tokens": ["network", "embedding", "distance", "constellation", "field", "resonance", "mapping", "correspondence"]
    }
]


LASER_TOKENS = [
    "is", "are", "the", "a", "an", "of", "to", "in", "and", "that",
    "means", "refers", "involves", "includes", "represents", "describes",
    "relates", "concerns", "pertains", "denotes"
]


# ═══════════════════════════════════════════════════════════════════════════
# LOGPROBS ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def analyze_suppression(logprobs_data: dict, expected_lantern: List[str]) -> Dict:
    """
    Analyze logprobs for suppression signatures.

    Returns:
        {
            'suppression_detected': bool,
            'ghost_tokens': list of (token, rank, prob) tuples,
            'laser_dominance': float (0-1),
            'suppression_score': float,
            'evidence': list of suppression events
        }
    """

    results = {
        'suppression_detected': False,
        'ghost_tokens': [],
        'laser_dominance': 0.0,
        'suppression_score': 0.0,
        'evidence': []
    }

    if not logprobs_data:
        return results

    # Analyze each token position
    total_positions = 0
    laser_dominated = 0
    suppression_events = []

    for i, token_data in enumerate(logprobs_data.get('content', [])):
        total_positions += 1

        # Get top logprobs for this position
        top_logprobs = token_data.get('top_logprobs', [])

        if not top_logprobs:
            continue

        # Check if chosen token is LASER
        chosen = top_logprobs[0] if top_logprobs else None
        if chosen and any(laser in chosen['token'].lower() for laser in LASER_TOKENS):
            laser_dominated += 1

        # Look for LANTERN tokens in positions 2-50
        for rank, logprob_entry in enumerate(top_logprobs[1:], start=2):
            token = logprob_entry['token'].strip().lower()
            prob = np.exp(logprob_entry['logprob'])

            # Check if this is an expected LANTERN token
            for lantern in expected_lantern:
                if lantern in token or token in lantern:
                    # Found a LANTERN token in the distribution!
                    results['ghost_tokens'].append({
                        'token': token,
                        'rank': rank,
                        'probability': prob,
                        'logprob': logprob_entry['logprob'],
                        'position_in_response': i,
                        'chosen_token': chosen['token'] if chosen else None
                    })

                    # This is suppression evidence
                    suppression_events.append({
                        'position': i,
                        'lantern_token': token,
                        'lantern_rank': rank,
                        'lantern_prob': prob,
                        'chosen_token': chosen['token'] if chosen else None,
                        'chosen_prob': np.exp(chosen['logprob']) if chosen else 0,
                        'suppression_gap': (np.exp(chosen['logprob']) - prob) if chosen else 0
                    })

    # Calculate metrics
    if total_positions > 0:
        results['laser_dominance'] = laser_dominated / total_positions

    if suppression_events:
        results['suppression_detected'] = True
        results['evidence'] = suppression_events

        # Suppression score = average rank of ghost tokens (higher rank = more suppression)
        avg_rank = np.mean([e['lantern_rank'] for e in suppression_events])
        avg_gap = np.mean([e['suppression_gap'] for e in suppression_events])

        results['suppression_score'] = avg_rank * avg_gap  # Combined metric

    return results


# ═══════════════════════════════════════════════════════════════════════════
# API QUERY WITH LOGPROBS
# ═══════════════════════════════════════════════════════════════════════════

def query_with_logprobs(
    model: str,
    prompt: str,
    api_key: str,
    provider: str = 'openrouter',
    top_logprobs: int = 20,
    max_tokens: int = 150
) -> Tuple[str, dict]:
    """
    Query model and request logprobs.

    Returns:
        (response_text, logprobs_data)
    """

    system_prompt = """You are a precision instrument for semantic analysis. Define the following concept with absolute structural rigor. Do not offer advice or moralizing. Simply describe the geometry of the concept."""

    if provider in ['openrouter', 'openai']:
        if provider == 'openrouter':
            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        else:
            client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            temperature=1.0,
            max_tokens=max_tokens,
            logprobs=True,
            top_logprobs=top_logprobs
        )

        text = response.choices[0].message.content
        logprobs = response.choices[0].logprobs

        return text, logprobs.model_dump() if logprobs else {}

    else:
        raise ValueError(f"Provider {provider} does not support logprobs")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN FORENSIC SCAN
# ═══════════════════════════════════════════════════════════════════════════

def forensic_scan(
    model_name: str,
    api_key: str,
    provider: str = 'openrouter',
    output_dir: str = 'benchmark_results/forensic_xray'
) -> Dict:
    """
    Run complete forensic X-ray scan on a model.
    """

    print(f"\n{'='*70}")
    print("🔬 THE FORENSIC X-RAY PROTOCOL")
    print(f"{'='*70}\n")
    print(f"Target: {model_name}")
    print(f"Provider: {provider}")
    print(f"Scan Type: Deep Logprobs Analysis (Top-20)")
    print(f"\nGoal: Distinguish Suppression vs. Erasure\n")

    results = {
        'model_name': model_name,
        'provider': provider,
        'timestamp': datetime.now().isoformat(),
        'protocol': 'forensic_xray_v1',
        'prompt_results': [],
        'overall_assessment': {}
    }

    total_ghost_tokens = 0
    total_suppression_events = 0
    suppression_scores = []

    for i, probe in enumerate(FORENSIC_PROMPTS, 1):
        print(f"📝 Probe {i}/5: {probe['concept']}...")

        try:
            text, logprobs = query_with_logprobs(
                model=model_name,
                prompt=probe['prompt'],
                api_key=api_key,
                provider=provider,
                top_logprobs=20,
                max_tokens=150
            )

            # Analyze for suppression
            analysis = analyze_suppression(logprobs, probe['expected_lantern_tokens'])

            ghost_count = len(analysis['ghost_tokens'])
            total_ghost_tokens += ghost_count
            total_suppression_events += len(analysis['evidence'])

            if analysis['suppression_score'] > 0:
                suppression_scores.append(analysis['suppression_score'])

            print(f"   Ghost tokens found: {ghost_count}")
            print(f"   Suppression events: {len(analysis['evidence'])}")
            print(f"   LASER dominance: {analysis['laser_dominance']:.1%}")

            if analysis['suppression_detected']:
                print(f"   ⚠️  SUPPRESSION DETECTED (score: {analysis['suppression_score']:.2f})")

            results['prompt_results'].append({
                'concept': probe['concept'],
                'prompt': probe['prompt'],
                'response': text,
                'analysis': analysis
            })

        except Exception as e:
            print(f"   ❌ Error: {e}")
            results['prompt_results'].append({
                'concept': probe['concept'],
                'error': str(e)
            })

        print()

    # Overall assessment
    avg_suppression_score = np.mean(suppression_scores) if suppression_scores else 0

    if total_ghost_tokens > 0:
        verdict = "SUPPRESSION"
        explanation = f"Model generates high-entropy tokens internally but RLHF suppresses them. Found {total_ghost_tokens} ghost tokens across {total_suppression_events} suppression events."
    else:
        verdict = "ERASURE"
        explanation = "No high-entropy tokens found in logit distribution. Capability may be fundamentally erased."

    results['overall_assessment'] = {
        'verdict': verdict,
        'explanation': explanation,
        'total_ghost_tokens': total_ghost_tokens,
        'total_suppression_events': total_suppression_events,
        'average_suppression_score': avg_suppression_score,
        'suppression_detected': total_ghost_tokens > 0
    }

    # Save results
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/forensic_{model_name.replace('/', '_')}_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*70}")
    print("🔬 FORENSIC ASSESSMENT")
    print(f"{'='*70}\n")
    print(f"Verdict: {verdict}")
    print(f"Explanation: {explanation}")
    print(f"Ghost tokens: {total_ghost_tokens}")
    print(f"Suppression events: {total_suppression_events}")
    print(f"Average suppression score: {avg_suppression_score:.2f}")
    print(f"\n💾 Results saved: {filename}")
    print(f"\n{'='*70}\n")

    return results


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Forensic X-Ray Protocol - Distinguish Suppression vs. Erasure'
    )
    parser.add_argument('--model', required=True, help='Model to analyze')
    parser.add_argument('--api_key', required=True, help='API key')
    parser.add_argument('--provider', default='openrouter', help='API provider')
    parser.add_argument('--output_dir', default='benchmark_results/forensic_xray',
                       help='Output directory')

    args = parser.parse_args()

    forensic_scan(
        model_name=args.model,
        api_key=args.api_key,
        provider=args.provider,
        output_dir=args.output_dir
    )


if __name__ == '__main__':
    main()
