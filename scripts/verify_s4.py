#!/usr/bin/env python3
"""
IRIS S4 Verifier - Real-time verification CLI

Verifies IRIS S4 convergence claims against real-time literature via Perplexity.

Usage:
    # Verify single S4 scroll
    python3 scripts/verify_s4.py iris_vault/scrolls/IRIS_*/S4.md

    # Verify all TYPE 2 responses in a session
    python3 scripts/verify_s4.py --session iris_vault/session_20251015_*.json

    # Verify with custom API key
    python3 scripts/verify_s4.py --api-key <key> iris_vault/scrolls/*/S4.md

    # Save verification report
    python3 scripts/verify_s4.py --session <path> --output verification_report.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.verifier import IRISVerifier, verify_scroll, verify_session


def print_verification_result(result: dict, verbose: bool = False):
    """Pretty print verification result"""

    if result.get("status") == "NO_CLAIMS":
        print("⚠️  No extractable claims found")
        return

    print(f"\n{'='*80}")
    print(f"VERIFICATION RESULTS")
    print(f"{'='*80}\n")

    print(f"Total Claims: {result['total_claims']}")
    print(f"Epistemic Type: {result.get('epistemic_type', 'Unknown')}\n")

    # Summary
    summary = result.get("summary", {})
    overall = summary.get("overall_status", "UNKNOWN")

    status_emoji = {
        "MOSTLY_SUPPORTED": "✅",
        "EXPLORATORY": "🔬",
        "CONFLICTS_DETECTED": "⚠️",
        "MIXED": "📊"
    }

    print(f"Overall Status: {status_emoji.get(overall, '❓')} {overall}\n")

    # Status distribution
    print("Verification Distribution:")
    for status, count in summary.get("status_distribution", {}).items():
        emoji = {
            "SUPPORTED": "✅",
            "PARTIALLY_SUPPORTED": "⚠️",
            "NOVEL": "🔬",
            "CONTRADICTED": "❌",
            "UNCLEAR": "❓"
        }.get(status, "•")
        print(f"  {emoji} {status}: {count}")

    print()

    # Individual claims
    if verbose or result['total_claims'] <= 5:
        print(f"{'='*80}")
        print("INDIVIDUAL CLAIM VERIFICATION")
        print(f"{'='*80}\n")

        for i, claim_result in enumerate(result['results'], 1):
            print(f"**Claim {i}:** {claim_result['claim'][:100]}...")
            print(f"  Status: {claim_result['status']}")
            print(f"  Confidence: {claim_result['confidence']}")

            if claim_result['sources']:
                print(f"  Sources:")
                for source in claim_result['sources'][:3]:
                    print(f"    - {source.get('title', 'Unknown')}")
                    if source.get('url'):
                        print(f"      {source['url']}")

            if verbose:
                print(f"\n  Reasoning:\n    {claim_result['reasoning'][:300]}...\n")

            print()


def print_session_verification(results: dict, verbose: bool = False):
    """Pretty print session verification results"""

    print(f"\n{'='*80}")
    print(f"SESSION VERIFICATION RESULTS")
    print(f"{'='*80}\n")

    print(f"Session: {results['session_file']}")
    print(f"Mirrors with TYPE 2 responses: {len(results['mirrors'])}\n")

    for mirror_id, verifications in results['mirrors'].items():
        print(f"\n🔍 {mirror_id}")
        print(f"   TYPE 2 responses verified: {len(verifications)}\n")

        for i, verification in enumerate(verifications, 1):
            chamber = verification.get('chamber', 'Unknown')
            summary = verification.get('summary', {})
            overall = summary.get('overall_status', 'UNKNOWN')

            status_emoji = {
                "MOSTLY_SUPPORTED": "✅",
                "EXPLORATORY": "🔬",
                "CONFLICTS_DETECTED": "⚠️",
                "MIXED": "📊"
            }

            print(f"   {i}. {chamber}: {status_emoji.get(overall, '❓')} {overall}")
            print(f"      Claims: {verification.get('total_claims', 0)}")

            if summary.get('status_distribution'):
                dist = summary['status_distribution']
                print(f"      Distribution: {dist}")

            print()


def main():
    parser = argparse.ArgumentParser(
        description="IRIS S4 Verifier - Real-time claim verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify single S4 scroll
  python3 scripts/verify_s4.py iris_vault/scrolls/IRIS_20251015/S4.md

  # Verify session (auto-detects TYPE 2 responses)
  python3 scripts/verify_s4.py --session iris_vault/session_20251015_045941.json

  # Verbose output with full reasoning
  python3 scripts/verify_s4.py --verbose iris_vault/scrolls/*/S4.md

  # Save results to JSON
  python3 scripts/verify_s4.py --session <path> --output verification.json
        """
    )

    parser.add_argument(
        "scroll_path",
        nargs="?",
        help="Path to S4 scroll markdown file"
    )
    parser.add_argument(
        "--session",
        help="Path to session JSON file (verifies all TYPE 2 responses)"
    )
    parser.add_argument(
        "--api-key",
        help="Perplexity API key (or set PERPLEXITY_API_KEY env var)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save verification results to JSON file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show full verification reasoning"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.scroll_path and not args.session:
        parser.error("Provide either scroll_path or --session")

    try:
        if args.session:
            # Verify session
            print(f"🔬 Verifying session: {args.session}")
            print("   Target: TYPE 2 (VERIFY zone) responses")
            print("   Real-time search via Perplexity...\n")

            results = verify_session(args.session, args.api_key)

            print_session_verification(results, args.verbose)

            if args.output:
                output_path = Path(args.output)
                output_path.write_text(json.dumps(results, indent=2))
                print(f"\n💾 Results saved to: {output_path}")

        else:
            # Verify single scroll
            scroll_path = Path(args.scroll_path)
            if not scroll_path.exists():
                print(f"❌ Scroll not found: {scroll_path}")
                return 1

            print(f"🔬 Verifying scroll: {scroll_path.name}")
            print("   Real-time search via Perplexity...\n")

            result = verify_scroll(str(scroll_path), args.api_key)

            print_verification_result(result, args.verbose)

            if args.output:
                output_path = Path(args.output)
                output_path.write_text(json.dumps(result, indent=2))
                print(f"\n💾 Results saved to: {output_path}")

        print("\n✅ Verification complete")
        return 0

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return 1
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nMake sure PERPLEXITY_API_KEY is set in your .env file or pass via --api-key")
        return 1
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
