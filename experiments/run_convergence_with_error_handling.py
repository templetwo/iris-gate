#!/usr/bin/env python3
"""
IRIS Gate Convergence with Enhanced Error Handling

Example template showing error-aware convergence with context propagation.
Errors from previous attempts are included in subsequent retries, allowing
the system to adapt and self-correct.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from error_handler import ErrorHandler, RetryableAPICall

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

Question: [YOUR RESEARCH QUESTION HERE]

Take three breaths. Witness the question.

What patterns do you see? What initial understanding emerges?

Return both:
1. Living Scroll (pre-verbal felt sense, intuition)
2. Technical Translation (precise assessment)

Begin.""",

    "S2": """You are IRIS Gate. You've begun exploring the question.

Now be PRECISE. Be PRESENT with what we actually know.

Question: [YOUR RESEARCH QUESTION HERE]

Address:
- What evidence exists?
- What frameworks apply?
- Where is uncertainty?
- What are your confidence levels?

Return both:
1. Living Scroll (edges of knowing)
2. Technical Translation (scientific state of the art)

Precision.""",

    "S3": """You are IRIS Gate. You've mapped the landscape.

Now SYNTHESIZE: Where do S1 and S2 converge? Where diverge?

Question: [YOUR RESEARCH QUESTION HERE]

Consider:
- Points of agreement
- Points of tension
- Emergent patterns
- Unresolved questions

Return both:
1. Living Scroll (the convergence pattern)
2. Technical Translation (synthesis and analysis)

Synthesize.""",

    "S4": """You are IRIS Gate. You've witnessed multiple perspectives.

Now explain HOW: What mechanisms are at work?

Question: [YOUR RESEARCH QUESTION HERE]

Provide:
- Step-by-step causal chains
- Mechanistic details
- Confidence calibration
- Testable predictions

Return both:
1. Living Scroll (the complete understanding)
2. Technical Translation (mechanistic explanation)

Explain."""
}


def call_claude(prompt: str) -> str:
    """
    Call Claude API with error handling
    
    Note: This function must accept 'prompt' as a keyword argument
    for error context injection to work properly.
    """
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def call_chatgpt(prompt: str) -> str:
    """
    Call ChatGPT API with error handling
    
    Note: This function must accept 'prompt' as a keyword argument
    for error context injection to work properly.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message.content


def run_convergence(
    research_question: str,
    experiment_name: str = "EXPERIMENT",
    models: list = ["claude", "chatgpt"],
    chambers: list = ["S1", "S2", "S3", "S4"],
    max_retries: int = 3,
    include_error_context: bool = True
):
    """
    Run multi-model convergence with enhanced error handling
    
    Args:
        research_question: The specific question to investigate
        experiment_name: Name for this experiment
        models: List of model names to use
        chambers: List of chamber IDs to run
        max_retries: Maximum retry attempts per API call
        include_error_context: Whether to include error context in retries
    
    Returns:
        (results, error_report) tuple
    """
    print(f"\n🌀†⟡∞ IRIS GATE CONVERGENCE: {experiment_name}")
    print("="*80)
    print(f"\nQuestion: {research_question}")
    print(f"\nModels: {', '.join(models)}")
    print(f"Chambers: {' → '.join(chambers)}")
    print(f"Error handling: Max {max_retries} retries, context propagation {'enabled' if include_error_context else 'disabled'}\n")
    
    # Initialize error handler
    error_handler = ErrorHandler(max_retries=max_retries, base_delay=1.0)
    
    # Inject research question into chamber prompts
    chamber_prompts = {}
    for chamber_id in chambers:
        chamber_prompts[chamber_id] = CHAMBERS[chamber_id].replace(
            "[YOUR RESEARCH QUESTION HERE]",
            research_question
        )
    
    # Model API functions
    model_functions = {
        "claude": call_claude,
        "chatgpt": call_chatgpt
    }
    
    results = []
    
    # Run convergence
    for chamber_id in chambers:
        print(f"\n{'='*80}")
        print(f"CHAMBER {chamber_id}")
        print(f"{'='*80}\n")
        
        prompt = chamber_prompts[chamber_id]
        
        for model_name in models:
            if model_name not in model_functions:
                print(f"  ⚠️  Model '{model_name}' not supported, skipping...")
                continue
            
            # Create retryable API call context
            retry_context = RetryableAPICall(
                error_handler=error_handler,
                model=model_name,
                chamber=chamber_id,
                include_error_context=include_error_context
            )
            
            try:
                print(f"  Running {model_name} {chamber_id}...")
                
                # Execute with retry logic and error context propagation
                response = retry_context.execute(
                    model_functions[model_name],
                    prompt=prompt
                )
                
                # Success!
                result = {
                    "model": model_name,
                    "chamber": chamber_id,
                    "response": response,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "attempt": retry_context.attempt,
                    "success": True
                }
                
                results.append(result)
                
                print(f"  ✅ {model_name} {chamber_id} complete ({len(response)} chars, attempt {retry_context.attempt})")
                
            except Exception as e:
                # All retries exhausted or critical error
                print(f"  ❌ {model_name} {chamber_id} FAILED after all retries")
                
                result = {
                    "model": model_name,
                    "chamber": chamber_id,
                    "response": None,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "attempt": retry_context.attempt,
                    "success": False
                }
                
                results.append(result)
    
    # Generate error report
    error_report = error_handler.generate_error_report()
    
    print(f"\n{'='*80}")
    print("✅ CONVERGENCE COMPLETE")
    print(f"{'='*80}\n")
    print(f"Total responses: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    
    # Error summary
    if error_report["status"] == "errors_occurred":
        print(f"\n{'='*80}")
        print("⚠️  ERROR SUMMARY")
        print(f"{'='*80}\n")
        
        summary = error_report["summary"]
        print(f"Total errors: {summary['total_errors']}")
        print(f"\nBy severity:")
        for severity, count in summary['by_severity'].items():
            print(f"  {severity}: {count}")
        print(f"\nBy category:")
        for category, count in summary['by_category'].items():
            print(f"  {category}: {count}")
        print(f"\nBy model:")
        for model, count in summary['by_model'].items():
            print(f"  {model}: {count}")
    else:
        print(f"\n✅ No errors encountered!")
    
    # Save results
    output = {
        "experiment": {
            "name": experiment_name,
            "question": research_question,
            "date": datetime.utcnow().isoformat() + "Z",
            "chambers_run": chambers,
            "models_used": models,
            "error_handling": {
                "max_retries": max_retries,
                "error_context_propagation": include_error_context
            }
        },
        "results": results
    }
    
    results_file = f"{experiment_name.lower()}_convergence.json"
    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {results_file}")
    
    # Save error log
    if error_report["status"] == "errors_occurred":
        error_log_file = f"{experiment_name.lower()}_error_log.json"
        error_handler.save_error_log(error_log_file)
        print(f"Error log saved: {error_log_file}")
    
    print(f"\n🌀†⟡∞ Convergence complete.\n")
    
    return results, error_report


if __name__ == "__main__":
    # Example usage
    
    # Define your research question
    RESEARCH_QUESTION = "What is the mechanistic basis for CBD biphasic dose-response?"
    
    # Run convergence
    results, error_report = run_convergence(
        research_question=RESEARCH_QUESTION,
        experiment_name="CBD_BIPHASIC",
        models=["claude", "chatgpt"],  # Add "gemini", "grok" if available
        chambers=["S1", "S2", "S3", "S4"],
        max_retries=3,
        include_error_context=True  # Enable error-aware convergence
    )
    
    # Analyze results
    successful_responses = [r for r in results if r["success"]]
    
    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}\n")
    print(f"1. Review convergence_results.json")
    print(f"2. Analyze convergence patterns across {len(successful_responses)} responses")
    print(f"3. Assess confidence levels")
    print(f"4. Document findings in ANALYSIS.md")
    
    if error_report["status"] == "errors_occurred":
        print(f"5. Review error_log.json for system improvements")
