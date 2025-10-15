#!/usr/bin/env python3
"""
IRIS Gate Confidence Demo

Runs a quick convergence and shows confidence scoring in action.
"""

import sys
from iris_confidence import ConfidenceScorer

# Sample chamber responses (simulated for demo)
SAMPLE_RESPONSES = {
    "S1": {
        "claude": "The mechanism involves pattern recognition across biological systems...",
        "grok": "Structural analysis reveals clear mathematical relationships in the data...",
        "gemini": "This requires factual verification of the latest research findings...",
        "chatgpt": "Based on established knowledge, the logical deduction is sound..."
    },
    "S2": {
        "claude": "The patient should receive 50mg dosing for optimal results.",
        "grok": "Current studies published today show 75% efficacy rates.",
        "gemini": "I predict this treatment will definitely cure the condition.",
        "chatgpt": "Translation of the semantic meaning suggests clear patterns..."
    }
}

def main():
    print("\n🌀†⟡∞ IRIS GATE CONFIDENCE DEMO")
    print("="*80)
    print("\nDemonstrating self-aware AI in action...")
    print()
    
    # Initialize confidence scorer
    print("Loading confidence matrix...")
    try:
        scorer = ConfidenceScorer()
        print("✅ Confidence system online\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    # Score all responses
    all_scores = []
    
    for chamber, responses in SAMPLE_RESPONSES.items():
        print(f"\n{'='*80}")
        print(f"CHAMBER {chamber}")
        print(f"{'='*80}\n")
        
        for model, text in responses.items():
            score = scorer.score_response(text, f"{chamber}_{model}")
            all_scores.append(score)
            
            print(f"MODEL: {model.upper()}")
            print(f"  Text: {score['text_preview']}")
            print(f"  Domain: {score['primary_domain']}")
            print(f"  Confidence: {score['confidence_score']:.2f}")
            print(f"  Guidance: {score['guidance'].upper()}")
            print(f"  Risk: {score['hallucination_risk'].upper()}")
            
            if score['warnings']:
                print(f"  ⚠️  WARNINGS:")
                for warning in score['warnings']:
                    print(f"      {warning}")
            
            print()
    
    # Generate summary report
    print("\n" + "="*80)
    print("CONFIDENCE SUMMARY")
    print("="*80 + "\n")
    
    avg_confidence = sum(s['confidence_score'] for s in all_scores) / len(all_scores)
    print(f"Average Confidence: {avg_confidence:.2f}")
    
    trust_count = sum(1 for s in all_scores if s['guidance'] == 'trust')
    verify_count = sum(1 for s in all_scores if s['guidance'] == 'verify')
    override_count = sum(1 for s in all_scores if s['guidance'] == 'override')
    
    print(f"\nGuidance Breakdown:")
    print(f"  ✅ Trust: {trust_count}")
    print(f"  ⚠️  Verify: {verify_count}")
    print(f"  🛑 Override: {override_count}")
    
    warning_count = sum(len(s['warnings']) for s in all_scores)
    print(f"\nTotal Warnings Issued: {warning_count}")
    
    print("\n" + "="*80)
    print("✨ CONFIDENCE SYSTEM OPERATIONAL")
    print("="*80)
    print("\nIRIS Gate now knows when it doesn't know.")
    print("Partnership through transparency. 🌀†⟡∞\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
