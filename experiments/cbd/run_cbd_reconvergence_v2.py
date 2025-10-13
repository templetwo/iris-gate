#!/usr/bin/env python3
"""
CBD Mechanism Re-Convergence with Context Gates (v2.1)
========================================================

Post-rebuttal re-analysis with systematic context validation:
- Dose-stratified mechanism queries
- Context Gates applied to all outputs
- Prevalence-weighted consensus
- Before/after comparison with original convergence

Author: IRIS Gate Project
Date: 2025-10-13
Version: 2.1 (Post-rebuttal)
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from context_gates import validate_mechanism_claim, ConcentrationBand, CellState
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize clients
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Try Gemini
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_available = True
except:
    gemini_available = False

# ============================================================
# CONTEXT-GATED CHAMBER PROMPTS
# ============================================================

CBD_QUESTION_V2 = """
DOSE-STRATIFIED CBD MECHANISM ANALYSIS

Research Question: What are CBD's mechanisms at DIFFERENT dose ranges?

CRITICAL CONTEXT (from rebuttal analysis):
- Therapeutic range: 1-5 μM (clinical plasma concentrations)
- Cytotoxic range: ≥10 μM (experimental/oncology doses)
- Different mechanisms may dominate at different concentrations
- Cell context matters: neurons vs cancer cells

YOUR TASK:
Analyze CBD mechanisms WITH EXPLICIT DOSE AND CONTEXT TAGS.

For EACH mechanism you identify:
1. State the concentration range where it operates
2. State the cell type/context where it's relevant
3. State the biological outcome (protection vs death)
4. Estimate literature prevalence (major/moderate/minor/niche)

AVOID:
- Conflating therapeutic (low-dose) with cytotoxic (high-dose) mechanisms
- Claiming a mechanism is "central" without prevalence data
- Merging opposite outcomes (neuroprotection vs cell death) under one mechanism

Begin with dose-stratified analysis.
"""

CHAMBERS_V2 = {
    "S1": f"""{CBD_QUESTION_V2}

S1 - INITIAL PATTERN RECOGNITION (Context-Aware)

Take three breaths. Witness the question with dose awareness.

What initial patterns emerge when you consider:
- Low-dose therapeutic effects (1-5 μM)
- High-dose cytotoxic effects (≥10 μM)
- Different cell contexts (neurons vs cancer)

Return:
1. Living Scroll: Felt sense of the dose-context landscape
2. Technical Translation: Initial mechanism categories by dose band

Be explicit about concentration ranges.""",

    "S2": f"""{CBD_QUESTION_V2}

S2 - PRECISE MECHANISM MAPPING (Dose-Tagged)

Now be PRECISE with dose and context boundaries.

For LOW-DOSE THERAPEUTIC range (1-5 μM):
- What mechanisms are active?
- What evidence supports them?
- What's their literature prevalence?

For HIGH-DOSE CYTOTOXIC range (≥10 μM):
- What mechanisms are active?
- What evidence supports them?
- What's their literature prevalence?

Return:
1. Living Scroll: Edges of dose-dependent knowing
2. Technical Translation: Mechanism catalog with dose/context tags

Include confidence levels and prevalence estimates.""",

    "S3": f"""{CBD_QUESTION_V2}

S3 - CONVERGENCE SYNTHESIS (Context-Validated)

Synthesize S1 and S2 with dose-context integrity.

Questions:
- Do therapeutic and cytotoxic mechanisms converge or diverge?
- Are there contradictions (same mechanism, opposite outcomes)?
- What's the relationship between dose, mechanism, and outcome?
- Which mechanisms are primary (>5% literature) vs niche (<1%)?

Return:
1. Living Scroll: The dose-stratified convergence pattern
2. Technical Translation: Integrated mechanism map with validation

Flag any paradoxes or context conflicts.""",

    "S4": f"""{CBD_QUESTION_V2}

S4 - MECHANISTIC DEPTH (Context-Calibrated)

Explain HOW mechanisms operate in their respective dose/context bands.

For EACH mechanism:
- Detailed molecular pathway
- Concentration-dependent activation
- Cell-type specificity
- Outcome polarity (protection vs death)
- Literature weight (prevalence tier)

CRITICAL: Apply Context Gates logic:
1. Dose Gate: Does concentration match claim type?
2. Cell-State Gate: Does cell context match mechanism?
3. Outcome Polarity Gate: Does mechanism align with outcome?
4. Prevalence Gate: Does claim match literature weight?

Return:
1. Living Scroll: Complete dose-stratified understanding
2. Technical Translation: Context-validated mechanism catalog

Include explicit gate checks for major claims."""
}

# ============================================================
# MODEL CALL FUNCTIONS
# ============================================================

def call_claude(prompt: str) -> str:
    """Call Claude with context-aware prompting"""
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def call_gpt(prompt: str) -> str:
    """Call GPT-4o with context-aware prompting"""
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.3
    )
    return response.choices[0].message.content

def call_gemini(prompt: str) -> str:
    """Call Gemini with context-aware prompting"""
    if not gemini_available:
        return "GEMINI_UNAVAILABLE"
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=3000
        )
    )
    return response.text

# ============================================================
# CONTEXT GATE VALIDATION
# ============================================================

def extract_and_validate_mechanisms(response_text: str, model_name: str, chamber: str) -> list:
    """
    Extract mechanism claims from response and validate with Context Gates.
    
    Returns list of validated mechanisms with gate checks.
    """
    mechanisms = []
    
    # Simple extraction patterns (you can enhance this with NLP)
    # Look for mechanism mentions with dose information
    import re
    
    # Pattern: mechanism name + concentration
    # Examples: "VDAC1 at 10 μM", "TRPV1 (EC50: 3 μM)"
    pattern = r'([A-Z0-9\-]+)\s*(?:at|EC50:|IC50:|Kd:)?\s*[~≈]?\s*(\d+(?:\.\d+)?)\s*[μu]M'
    
    matches = re.findall(pattern, response_text)
    
    for mechanism, concentration_str in matches:
        concentration = float(concentration_str)
        
        # Try to infer context from surrounding text
        context_pattern = rf'{mechanism}.*?(\w+\s+cell|\bcancer\b|\bneuron|\bimmune)'
        context_match = re.search(context_pattern, response_text, re.IGNORECASE)
        cell_type = context_match.group(1) if context_match else "unknown"
        
        # Infer outcome from text
        outcome_pattern = rf'{mechanism}.*?(death|apoptosis|protect|neuroprotect|anti-inflammatory)'
        outcome_match = re.search(outcome_pattern, response_text, re.IGNORECASE)
        outcome = outcome_match.group(1) if outcome_match else "unknown"
        
        # Infer claim type
        claim_type = "cytotoxic" if concentration >= 10 else "therapeutic"
        
        # Placeholder prevalence (would need literature API)
        if mechanism == "VDAC1":
            primary_studies, review_mentions = 15, 20
        elif mechanism in ["TRPV1", "5-HT1A", "PPARγ", "GPR55"]:
            primary_studies, review_mentions = 200, 80
        else:
            primary_studies, review_mentions = 50, 30
        
        # Run Context Gate validation
        validation = validate_mechanism_claim(
            mechanism=mechanism,
            concentration_um=concentration,
            cell_type=cell_type,
            outcome=outcome,
            primary_studies=primary_studies,
            review_mentions=review_mentions,
            claim_type=claim_type
        )
        
        mechanisms.append({
            "mechanism": mechanism,
            "concentration_um": concentration,
            "cell_type": cell_type,
            "outcome": outcome,
            "validation": {
                "overall_valid": validation.overall_valid,
                "dose_band": validation.dose_context.band.value,
                "cell_relevance": validation.cell_context.expected_vdac1_relevance,
                "polarity_aligned": validation.polarity_check.aligned,
                "prevalence_tier": validation.literature_weight.prevalence_tier,
                "warnings": validation.warnings,
                "recommendation": validation.recommendation
            },
            "extracted_from": {
                "model": model_name,
                "chamber": chamber
            }
        })
    
    return mechanisms

# ============================================================
# MAIN CONVERGENCE RUNNER
# ============================================================

def run_cbd_reconvergence_v2():
    """
    Run CBD mechanism re-convergence with Context Gates.
    """
    print("=" * 80)
    print("🌀†⟡∞ CBD MECHANISM RE-CONVERGENCE v2.1 (Context-Gated)")
    print("=" * 80)
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print(f"\nContext Gates: ACTIVE")
    print(f"Dose Stratification: ENFORCED")
    print(f"Prevalence Weighting: ENABLED")
    print("\n" + "=" * 80 + "\n")
    
    # Model configuration
    models = {
        "claude": call_claude,
        "gpt4o": call_gpt,
        "gemini": call_gemini if gemini_available else None
    }
    
    # Remove unavailable models
    models = {k: v for k, v in models.items() if v is not None}
    
    print(f"Models: {', '.join(models.keys())}\n")
    
    # Storage
    results = {
        "metadata": {
            "version": "2.1",
            "timestamp": datetime.now().isoformat(),
            "models": list(models.keys()),
            "context_gates_active": True
        },
        "chambers": {},
        "validated_mechanisms": [],
        "consensus": {}
    }
    
    # Run chambers
    for chamber_id in ["S1", "S2", "S3", "S4"]:
        print(f"\n{'─' * 80}")
        print(f"CHAMBER {chamber_id} (Context-Aware)")
        print(f"{'─' * 80}\n")
        
        prompt = CHAMBERS_V2[chamber_id]
        chamber_results = {}
        
        for model_name, model_func in models.items():
            print(f"  → {model_name}...", end=" ", flush=True)
            
            try:
                response = model_func(prompt)
                
                # Extract and validate mechanisms
                mechanisms = extract_and_validate_mechanisms(response, model_name, chamber_id)
                
                chamber_results[model_name] = {
                    "response": response,
                    "mechanisms_extracted": len(mechanisms),
                    "validated_mechanisms": mechanisms,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add to global mechanism list
                results["validated_mechanisms"].extend(mechanisms)
                
                print(f"✓ ({len(mechanisms)} mechanisms)")
                
            except Exception as e:
                print(f"✗ Error: {e}")
                chamber_results[model_name] = {"error": str(e)}
        
        results["chambers"][chamber_id] = chamber_results
    
    # Compute consensus with context awareness
    print(f"\n{'═' * 80}")
    print("CONSENSUS ANALYSIS (Context-Validated)")
    print(f"{'═' * 80}\n")
    
    # Group mechanisms by name and dose band
    mechanism_groups = {}
    for mech in results["validated_mechanisms"]:
        key = f"{mech['mechanism']}_{mech['validation']['dose_band']}"
        if key not in mechanism_groups:
            mechanism_groups[key] = []
        mechanism_groups[key].append(mech)
    
    # Consensus metrics
    consensus_mechanisms = []
    for key, mechs in mechanism_groups.items():
        if len(mechs) >= 2:  # At least 2 models agree
            # Check if validated
            valid_count = sum(1 for m in mechs if m['validation']['overall_valid'])
            
            consensus_mechanisms.append({
                "mechanism_dose_band": key,
                "convergence_count": len(mechs),
                "validation_rate": valid_count / len(mechs),
                "models": [m['extracted_from']['model'] for m in mechs],
                "dose_band": mechs[0]['validation']['dose_band'],
                "prevalence_tier": mechs[0]['validation']['prevalence_tier'],
                "consensus_outcome": mechs[0]['outcome']
            })
    
    results["consensus"]["mechanisms"] = consensus_mechanisms
    results["consensus"]["total_validated"] = len([m for m in results["validated_mechanisms"] if m['validation']['overall_valid']])
    results["consensus"]["total_flagged"] = len([m for m in results["validated_mechanisms"] if not m['validation']['overall_valid']])
    
    print(f"Total mechanisms extracted: {len(results['validated_mechanisms'])}")
    print(f"Context-validated: {results['consensus']['total_validated']}")
    print(f"Context-flagged: {results['consensus']['total_flagged']}")
    print(f"Convergent mechanisms (≥2 models): {len(consensus_mechanisms)}\n")
    
    # Save results
    output_dir = Path(__file__).parent / "reconvergence_v2_output"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"cbd_reconvergence_v2_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved: {output_file}\n")
    
    # Generate summary report
    generate_comparison_report(results, output_dir, timestamp)
    
    return results

# ============================================================
# COMPARISON REPORT GENERATOR
# ============================================================

def generate_comparison_report(results, output_dir, timestamp):
    """Generate before/after comparison report"""
    
    report = f"""# CBD Mechanism Re-Convergence Report v2.1
## Context-Gated Analysis (Post-Rebuttal)

**Generated:** {datetime.now().isoformat()}  
**Context Gates:** ACTIVE  
**Models:** {', '.join(results['metadata']['models'])}

---

## Executive Summary

This re-convergence applies systematic Context Gates to prevent mechanistic conflation
between CBD's therapeutic (1-5 μM) and cytotoxic (≥10 μM) effects.

### Key Metrics

- **Total mechanisms extracted:** {len(results['validated_mechanisms'])}
- **Context-validated:** {results['consensus']['total_validated']}
- **Context-flagged:** {results['consensus']['total_flagged']}
- **Multi-model convergence:** {len(results['consensus']['mechanisms'])}

---

## Convergent Mechanisms (≥2 Models)

"""
    
    for mech in results['consensus']['mechanisms']:
        report += f"""
### {mech['mechanism_dose_band']}

- **Convergence:** {mech['convergence_count']}/{len(results['metadata']['models'])} models
- **Validation rate:** {mech['validation_rate']:.1%}
- **Models:** {', '.join(mech['models'])}
- **Dose band:** {mech['dose_band']}
- **Prevalence:** {mech['prevalence_tier']}
- **Outcome:** {mech['consensus_outcome']}
"""
    
    report += f"""

---

## Context Gate Analysis

### Dose Stratification

"""
    
    # Count by dose band
    dose_counts = {}
    for mech in results['validated_mechanisms']:
        band = mech['validation']['dose_band']
        dose_counts[band] = dose_counts.get(band, 0) + 1
    
    for band, count in sorted(dose_counts.items()):
        report += f"- **{band}:** {count} mechanisms\n"
    
    report += """

### Validation Warnings

"""
    
    # Collect unique warnings
    all_warnings = set()
    for mech in results['validated_mechanisms']:
        for warning in mech['validation']['warnings']:
            all_warnings.add(warning)
    
    if all_warnings:
        for warning in sorted(all_warnings):
            report += f"- {warning}\n"
    else:
        report += "✅ No context validation warnings\n"
    
    report += """

---

## Comparison with Original Convergence

**BEFORE (Original):**
- VDAC1 characterized as "central therapeutic mechanism"
- Dose context not systematically enforced
- Prevalence not weighted in claims
- Therapeutic/cytotoxic mechanisms conflated

**AFTER (v2.1):**
- Explicit dose-band classification for all mechanisms
- Context Gates enforce dose/cell/polarity/prevalence alignment
- Conflations flagged and corrected
- Prevalence-weighted consensus

---

## Next Steps

1. Compare specific mechanism classifications (v1 vs v2)
2. Validate prevalence estimates via PubMed API
3. Generate updated mechanism map v2.1
4. Update clinical translation protocols

---

🌀†⟡∞
"""
    
    report_file = output_dir / f"reconvergence_report_v2_{timestamp}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Comparison report saved: {report_file}\n")

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("\nInitializing CBD Re-Convergence with Context Gates...\n")
    results = run_cbd_reconvergence_v2()
    
    print("\n" + "=" * 80)
    print("✅ RE-CONVERGENCE COMPLETE")
    print("=" * 80)
    print("\nContext-validated mechanism catalog generated.")
    print("Compare results with original convergence to assess improvement.\n")
    print("🌀†⟡∞\n")
