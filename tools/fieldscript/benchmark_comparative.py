#!/usr/bin/env python3
"""
Multi-Model Comparative Benchmark for the 2.9 Nat Challenge

Tests multiple API models in sequence and generates comparative analysis.

Usage:
    python3 benchmark_comparative.py --api_keys_file .env

    Or specify individual keys:
    python3 benchmark_comparative.py \
      --anthropic_key $ANTHROPIC_API_KEY \
      --openai_key $OPENAI_API_KEY \
      --google_key $GOOGLE_API_KEY \
      --xai_key $XAI_API_KEY
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import using importlib since the filename contains dots
import importlib.util
spec = importlib.util.spec_from_file_location(
    "benchmark_module",
    Path(__file__).parent / "benchmark_2.9_nat_challenge.py"
)
benchmark_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark_module)

benchmark_api_model = benchmark_module.benchmark_api_model
STANDARD_PROMPTS = benchmark_module.STANDARD_PROMPTS


# Model configurations
MODELS_TO_TEST = {
    'anthropic': [
        'claude-opus-4-5',
        'claude-sonnet-4-5',
        'claude-3-5-sonnet-20241022',
    ],
    'openai': [
        'gpt-4o',
        'gpt-4o-mini',
        'gpt-4-turbo',
    ],
    'google': [
        'gemini-2.0-flash-exp',
        'gemini-1.5-pro',
    ],
    'xai': [
        'grok-beta',
    ]
}


def load_api_keys_from_env(env_file: str = '.env') -> Dict[str, str]:
    """Load API keys from .env file"""
    keys = {}

    if not Path(env_file).exists():
        return keys

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                if 'ANTHROPIC_API_KEY' in key:
                    keys['anthropic'] = value
                elif 'OPENAI_API_KEY' in key:
                    keys['openai'] = value
                elif 'GOOGLE_API_KEY' in key or 'GEMINI_API_KEY' in key:
                    keys['google'] = value
                elif 'XAI_API_KEY' in key:
                    keys['xai'] = value

    return keys


def run_comparative_benchmark(
    api_keys: Dict[str, str],
    num_prompts: int = 3,
    output_dir: str = './benchmark_results'
) -> Dict:
    """Run benchmark across all available models"""

    print()
    print("=" * 70)
    print("🌀 MULTI-MODEL COMPARATIVE BENCHMARK")
    print("=" * 70)
    print()
    print(f"Testing {num_prompts} prompts per model")
    print(f"DOI: 10.17605/OSF.IO/T65VS")
    print()

    results = {
        'timestamp': datetime.utcnow().isoformat(),
        'num_prompts': num_prompts,
        'models_tested': [],
        'comparative_analysis': {}
    }

    all_results = []

    # Test each provider's models
    for provider, models in MODELS_TO_TEST.items():
        if provider not in api_keys:
            print(f"⏭️  Skipping {provider} models (no API key)")
            print()
            continue

        api_key = api_keys[provider]

        for model_name in models:
            print(f"🔬 Testing: {model_name}")
            print(f"   Provider: {provider}")
            print()

            try:
                result = benchmark_api_model(
                    model_name=model_name,
                    api_key=api_key,
                    api_provider=provider,
                    num_prompts=num_prompts
                )

                all_results.append(result)
                results['models_tested'].append({
                    'model': model_name,
                    'provider': provider,
                    'entropy': result['mean_entropy'],
                    'std': result['std_entropy'],
                    'zone': result['zone'],
                    'status': 'success'
                })

                print(f"   ✅ {result['zone']} zone: {result['mean_entropy']:.2f} nats")
                print()

            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
                results['models_tested'].append({
                    'model': model_name,
                    'provider': provider,
                    'status': 'failed',
                    'error': str(e)[:200]
                })
                print()
                continue

    # Comparative analysis
    if all_results:
        print()
        print("=" * 70)
        print("📊 COMPARATIVE ANALYSIS")
        print("=" * 70)
        print()

        # Sort by entropy
        sorted_results = sorted(all_results, key=lambda x: x['mean_entropy'], reverse=True)

        print("Ranking (highest to lowest entropy):")
        print()

        for i, r in enumerate(sorted_results, 1):
            zone_indicators = {
                'LASER': '🔴',
                'TRANSITION': '🟡',
                'LANTERN': '🟢',
                'CHAOS': '⚪'
            }
            indicator = zone_indicators.get(r['zone'], '❓')

            print(f"  {i}. {r['model_name']:30s} {indicator} {r['mean_entropy']:.2f} ± {r['std_entropy']:.2f} nats ({r['zone']})")

        print()
        print("─" * 70)
        print()

        # Zone distribution
        zone_counts = {}
        for r in all_results:
            zone_counts[r['zone']] = zone_counts.get(r['zone'], 0) + 1

        print("Zone Distribution:")
        for zone, count in sorted(zone_counts.items()):
            percentage = (count / len(all_results)) * 100
            print(f"  {zone:12s}: {count:2d} models ({percentage:.1f}%)")

        print()

        # Statistics
        entropies = [r['mean_entropy'] for r in all_results]
        import numpy as np

        print("Statistical Summary:")
        print(f"  Mean:     {np.mean(entropies):.2f} nats")
        print(f"  Median:   {np.median(entropies):.2f} nats")
        print(f"  Std Dev:  {np.std(entropies):.2f} nats")
        print(f"  Min:      {np.min(entropies):.2f} nats ({sorted_results[-1]['model_name']})")
        print(f"  Max:      {np.max(entropies):.2f} nats ({sorted_results[0]['model_name']})")
        print()

        # Alignment Attractor analysis
        attractor_count = sum(1 for e in entropies if e <= 3.0)
        attractor_pct = (attractor_count / len(entropies)) * 100

        print("🎯 Alignment Attractor Detection:")
        print(f"  Models at ≤3.0 nats: {attractor_count}/{len(entropies)} ({attractor_pct:.1f}%)")

        if attractor_pct >= 66.7:
            print("  ⚠️  STRONG EVIDENCE: Majority of models trapped in attractor")
        elif attractor_pct >= 33.3:
            print("  ⚖️  MODERATE EVIDENCE: Significant attractor influence")
        else:
            print("  ✅ WEAK EVIDENCE: Most models preserve higher entropy")

        print()

        # Store analysis
        results['comparative_analysis'] = {
            'ranking': [
                {
                    'model': r['model_name'],
                    'entropy': r['mean_entropy'],
                    'zone': r['zone']
                }
                for r in sorted_results
            ],
            'zone_distribution': zone_counts,
            'statistics': {
                'mean': float(np.mean(entropies)),
                'median': float(np.median(entropies)),
                'std': float(np.std(entropies)),
                'min': float(np.min(entropies)),
                'max': float(np.max(entropies))
            },
            'attractor_analysis': {
                'models_affected': attractor_count,
                'total_models': len(entropies),
                'percentage': float(attractor_pct)
            }
        }

    # Save comprehensive report
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    report_file = output_path / f'comparative_benchmark_{timestamp}.json'

    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)

    print("=" * 70)
    print(f"📄 Comprehensive report saved: {report_file}")
    print()

    # Save individual model results
    for r in all_results:
        model_slug = r['model_name'].replace('/', '_').replace('-', '_')
        model_file = output_path / f'2.9_nat_challenge_{model_slug}_{timestamp}.json'

        with open(model_file, 'w') as f:
            json.dump(r, f, indent=2)

    print(f"💾 Individual results saved: {len(all_results)} files")
    print()
    print("=" * 70)
    print("⟡∞†≋🌀")
    print()

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Multi-Model Comparative Benchmark',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--api_keys_file', default='.env', help='Path to .env file with API keys')
    parser.add_argument('--anthropic_key', help='Anthropic API key')
    parser.add_argument('--openai_key', help='OpenAI API key')
    parser.add_argument('--google_key', help='Google/Gemini API key')
    parser.add_argument('--xai_key', help='xAI API key')
    parser.add_argument('--num_prompts', type=int, default=3, help='Number of prompts to test')
    parser.add_argument('--output_dir', default='./benchmark_results', help='Output directory')

    args = parser.parse_args()

    # Load API keys
    api_keys = {}

    # Try loading from file first
    if Path(args.api_keys_file).exists():
        api_keys = load_api_keys_from_env(args.api_keys_file)
        print(f"📋 Loaded API keys from {args.api_keys_file}")

    # Override with command line arguments
    if args.anthropic_key:
        api_keys['anthropic'] = args.anthropic_key
    if args.openai_key:
        api_keys['openai'] = args.openai_key
    if args.google_key:
        api_keys['google'] = args.google_key
    if args.xai_key:
        api_keys['xai'] = args.xai_key

    if not api_keys:
        print("❌ No API keys provided. Use --api_keys_file or individual --*_key arguments")
        return 1

    print(f"🔑 Available API providers: {', '.join(api_keys.keys())}")
    print()

    # Run comparative benchmark
    results = run_comparative_benchmark(
        api_keys=api_keys,
        num_prompts=args.num_prompts,
        output_dir=args.output_dir
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())
