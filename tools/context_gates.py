#!/usr/bin/env python3
"""
IRIS Gate Context Gates Framework
===================================

Prevents mechanistic conflation by enforcing four validation gates:
1. Dose Gate: Tags citations with concentration bands
2. Cell-State Gate: Classifies cell type/state vulnerability
3. Outcome Polarity Gate: Aligns mechanism with outcome
4. Prevalence Gate: Computes Literature Weight Index

Developed in response to CBD-VDAC1 rebuttal analysis (2025-10-13)
Ensures dose-concordant, context-aware mechanism interpretation.

Author: IRIS Gate Project
Version: 1.0
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re

# ============================================================
# DOSE GATE - Concentration Band Classification
# ============================================================

class ConcentrationBand(Enum):
    """Concentration ranges with therapeutic relevance"""
    ULTRA_LOW = "≤1 μM"      # Below therapeutic threshold
    THERAPEUTIC = "1-5 μM"    # Clinical therapeutic range
    SUPRA_THERAPEUTIC = "5-10 μM"  # Above typical therapy
    CYTOTOXIC = "≥10 μM"     # High-dose cytotoxic range

@dataclass
class DoseContext:
    """Citation dose context"""
    concentration_um: float
    band: ConcentrationBand
    therapeutic_concordant: bool  # True if dose matches therapeutic claims
    
def classify_dose(concentration_um: float, claim_type: str) -> DoseContext:
    """
    Classify dose and check therapeutic concordance.
    
    Args:
        concentration_um: Experimental concentration in μM
        claim_type: "therapeutic" or "cytotoxic"
    
    Returns:
        DoseContext with band classification and concordance flag
    """
    # Determine band
    if concentration_um <= 1.0:
        band = ConcentrationBand.ULTRA_LOW
    elif concentration_um <= 5.0:
        band = ConcentrationBand.THERAPEUTIC
    elif concentration_um <= 10.0:
        band = ConcentrationBand.SUPRA_THERAPEUTIC
    else:
        band = ConcentrationBand.CYTOTOXIC
    
    # Check concordance
    if claim_type == "therapeutic":
        concordant = concentration_um <= 5.0
    elif claim_type == "cytotoxic":
        concordant = concentration_um >= 10.0
    else:
        concordant = False
    
    return DoseContext(
        concentration_um=concentration_um,
        band=band,
        therapeutic_concordant=concordant
    )

def extract_concentration(text: str) -> Optional[float]:
    """
    Extract concentration from text using regex patterns.
    
    Args:
        text: Citation or abstract text
    
    Returns:
        Concentration in μM, or None if not found
    """
    patterns = [
        r'(\d+\.?\d*)\s*[μu]M',  # Standard μM notation
        r'(\d+\.?\d*)\s*μmol',   # μmol/L notation
        r'(\d+\.?\d*)\s*micromolar',  # Full word
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    
    return None

# ============================================================
# CELL-STATE GATE - Context Classification
# ============================================================

class CellState(Enum):
    """Cell type and activation state categories"""
    HEALTHY_NEURON = "healthy_neuron"
    RESTING_IMMUNE = "resting_immune"
    ACTIVATED_IMMUNE = "activated_immune"
    CANCER_CELL = "cancer_cell"
    STRESSED_NORMAL = "stressed_normal"
    UNKNOWN = "unknown"

@dataclass
class CellContext:
    """Cell type context for mechanism interpretation"""
    cell_state: CellState
    vdac1_expression: str  # "low", "normal", "high"
    metabolic_stress: str  # "low", "moderate", "high"
    expected_vdac1_relevance: str  # "minimal", "moderate", "high"

def classify_cell_context(cell_type: str, activation: str = "resting") -> CellContext:
    """
    Classify cell context and predict VDAC1 relevance.
    
    Args:
        cell_type: Cell type (e.g., "neuron", "cancer", "immune")
        activation: Activation state ("resting", "activated", "stressed")
    
    Returns:
        CellContext with VDAC1 relevance prediction
    """
    cell_type = cell_type.lower()
    activation = activation.lower()
    
    # Determine cell state
    if "neuron" in cell_type and activation == "resting":
        state = CellState.HEALTHY_NEURON
        vdac1_expr = "normal"
        stress = "low"
        vdac1_rel = "minimal"
    elif "immune" in cell_type and activation == "resting":
        state = CellState.RESTING_IMMUNE
        vdac1_expr = "normal"
        stress = "low"
        vdac1_rel = "minimal"
    elif "immune" in cell_type and activation == "activated":
        state = CellState.ACTIVATED_IMMUNE
        vdac1_expr = "high"
        stress = "moderate"
        vdac1_rel = "moderate"
    elif "cancer" in cell_type or "tumor" in cell_type:
        state = CellState.CANCER_CELL
        vdac1_expr = "high"
        stress = "high"
        vdac1_rel = "high"
    elif "stressed" in activation:
        state = CellState.STRESSED_NORMAL
        vdac1_expr = "normal"
        stress = "moderate"
        vdac1_rel = "moderate"
    else:
        state = CellState.UNKNOWN
        vdac1_expr = "unknown"
        stress = "unknown"
        vdac1_rel = "unknown"
    
    return CellContext(
        cell_state=state,
        vdac1_expression=vdac1_expr,
        metabolic_stress=stress,
        expected_vdac1_relevance=vdac1_rel
    )

# ============================================================
# OUTCOME POLARITY GATE - Mechanism-Outcome Alignment
# ============================================================

class OutcomeType(Enum):
    """Biological outcome categories"""
    CELL_DEATH = "cell_death"
    NEUROPROTECTION = "neuroprotection"
    ANTI_INFLAMMATORY = "anti_inflammatory"
    METABOLIC_ENHANCEMENT = "metabolic_enhancement"
    METABOLIC_DYSFUNCTION = "metabolic_dysfunction"
    UNKNOWN = "unknown"

@dataclass
class PolarityCheck:
    """Mechanism-outcome polarity validation"""
    mechanism: str
    outcome: OutcomeType
    aligned: bool
    conflict_warning: Optional[str]

def check_polarity(mechanism: str, outcome: str) -> PolarityCheck:
    """
    Check if mechanism aligns with claimed outcome.
    
    Args:
        mechanism: Molecular mechanism (e.g., "VDAC1_closure")
        outcome: Biological outcome (e.g., "neuroprotection")
    
    Returns:
        PolarityCheck with alignment status and warnings
    """
    outcome = outcome.lower()
    mechanism = mechanism.lower()
    
    # Classify outcome
    if any(term in outcome for term in ["death", "apoptosis", "cytotoxic", "kill"]):
        outcome_type = OutcomeType.CELL_DEATH
    elif any(term in outcome for term in ["neuroprotect", "protect", "survival"]):
        outcome_type = OutcomeType.NEUROPROTECTION
    elif any(term in outcome for term in ["anti-inflammatory", "inflammation"]):
        outcome_type = OutcomeType.ANTI_INFLAMMATORY
    elif any(term in outcome for term in ["metabolic enhancement", "atp increase", "biogenesis"]):
        outcome_type = OutcomeType.METABOLIC_ENHANCEMENT
    elif any(term in outcome for term in ["dysfunction", "depolarization", "atp decrease"]):
        outcome_type = OutcomeType.METABOLIC_DYSFUNCTION
    else:
        outcome_type = OutcomeType.UNKNOWN
    
    # Check VDAC1-specific alignment
    if "vdac1" in mechanism:
        if outcome_type in [OutcomeType.CELL_DEATH, OutcomeType.METABOLIC_DYSFUNCTION]:
            aligned = True
            warning = None
        elif outcome_type in [OutcomeType.NEUROPROTECTION, OutcomeType.METABOLIC_ENHANCEMENT]:
            aligned = False
            warning = "⚠️ PARADOX: VDAC1 closure causes dysfunction, not protection"
        else:
            aligned = False
            warning = "⚠️ UNCLEAR: VDAC1 mechanism-outcome relationship ambiguous"
    else:
        # Other mechanisms - assume aligned unless specific rules added
        aligned = True
        warning = None
    
    return PolarityCheck(
        mechanism=mechanism,
        outcome=outcome_type,
        aligned=aligned,
        conflict_warning=warning
    )

# ============================================================
# PREVALENCE GATE - Literature Weight Index
# ============================================================

@dataclass
class LiteratureWeight:
    """Mechanism prevalence in literature"""
    mechanism: str
    primary_studies: int
    review_mentions: int
    total_cbd_studies: int
    literature_weight_index: float  # 0.0 to 1.0
    prevalence_tier: str  # "major", "moderate", "minor", "niche"

def compute_literature_weight(
    mechanism: str,
    primary_studies: int,
    review_mentions: int,
    total_cbd_studies: int = 5000
) -> LiteratureWeight:
    """
    Compute Literature Weight Index (LWI) for mechanism.
    
    Args:
        mechanism: Mechanism name (e.g., "VDAC1", "TRPV1")
        primary_studies: Number of primary research papers
        review_mentions: Number of comprehensive review mentions
        total_cbd_studies: Total CBD papers in literature
    
    Returns:
        LiteratureWeight with LWI score and tier classification
    """
    # Compute raw proportions
    study_proportion = primary_studies / total_cbd_studies
    review_proportion = review_mentions / 100  # Assume 100 major reviews
    
    # Weighted average (reviews weighted 2x primary studies)
    lwi = (study_proportion + 2 * review_proportion) / 3
    
    # Classify tier
    if lwi >= 0.05:  # ≥5%
        tier = "major"
    elif lwi >= 0.01:  # 1-5%
        tier = "moderate"
    elif lwi >= 0.003:  # 0.3-1%
        tier = "minor"
    else:
        tier = "niche"
    
    return LiteratureWeight(
        mechanism=mechanism,
        primary_studies=primary_studies,
        review_mentions=review_mentions,
        total_cbd_studies=total_cbd_studies,
        literature_weight_index=lwi,
        prevalence_tier=tier
    )

# ============================================================
# INTEGRATED CONTEXT VALIDATOR
# ============================================================

@dataclass
class ValidationResult:
    """Complete context validation result"""
    mechanism: str
    dose_context: DoseContext
    cell_context: CellContext
    polarity_check: PolarityCheck
    literature_weight: LiteratureWeight
    
    overall_valid: bool
    warnings: List[str]
    recommendation: str

def validate_mechanism_claim(
    mechanism: str,
    concentration_um: float,
    cell_type: str,
    outcome: str,
    primary_studies: int,
    review_mentions: int,
    claim_type: str = "therapeutic"
) -> ValidationResult:
    """
    Comprehensive context gate validation.
    
    Args:
        mechanism: Mechanism name (e.g., "VDAC1")
        concentration_um: Experimental concentration
        cell_type: Cell type tested
        outcome: Claimed biological outcome
        primary_studies: Literature count
        review_mentions: Review mention count
        claim_type: "therapeutic" or "cytotoxic"
    
    Returns:
        ValidationResult with all gate checks and recommendation
    """
    warnings = []
    
    # Gate 1: Dose Gate
    dose = classify_dose(concentration_um, claim_type)
    if not dose.therapeutic_concordant and claim_type == "therapeutic":
        warnings.append(
            f"❌ DOSE GATE: {dose.band.value} exceeds therapeutic range for {claim_type} claims"
        )
    
    # Gate 2: Cell-State Gate
    cell = classify_cell_context(cell_type)
    if mechanism.lower() == "vdac1" and cell.expected_vdac1_relevance == "minimal":
        warnings.append(
            f"⚠️ CELL-STATE GATE: VDAC1 relevance expected to be minimal in {cell.cell_state.value}"
        )
    
    # Gate 3: Outcome Polarity Gate
    polarity = check_polarity(mechanism, outcome)
    if not polarity.aligned and polarity.conflict_warning:
        warnings.append(f"❌ POLARITY GATE: {polarity.conflict_warning}")
    
    # Gate 4: Prevalence Gate
    lit_weight = compute_literature_weight(mechanism, primary_studies, review_mentions)
    if lit_weight.prevalence_tier == "niche" and claim_type == "therapeutic":
        warnings.append(
            f"⚠️ PREVALENCE GATE: {mechanism} represents {lit_weight.prevalence_tier} "
            f"mechanism (LWI={lit_weight.literature_weight_index:.1%}), not primary pathway"
        )
    
    # Overall validation
    critical_failures = sum(1 for w in warnings if w.startswith("❌"))
    overall_valid = critical_failures == 0
    
    # Recommendation
    if overall_valid:
        recommendation = f"✅ VALIDATED: {mechanism} claim supported by context gates"
    elif critical_failures == 1:
        recommendation = f"⚠️ REFRAME: {mechanism} claim requires context restriction"
    else:
        recommendation = f"❌ REJECT: {mechanism} claim fails multiple context gates"
    
    return ValidationResult(
        mechanism=mechanism,
        dose_context=dose,
        cell_context=cell,
        polarity_check=polarity,
        literature_weight=lit_weight,
        overall_valid=overall_valid,
        warnings=warnings,
        recommendation=recommendation
    )

# ============================================================
# EXAMPLE USAGE & TESTING
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("IRIS Gate Context Gates Framework - Test Suite")
    print("=" * 60)
    print()
    
    # Test Case 1: VDAC1 in cancer cells (VALID)
    print("Test 1: VDAC1 cytotoxic mechanism in cancer cells")
    print("-" * 60)
    result1 = validate_mechanism_claim(
        mechanism="VDAC1",
        concentration_um=10.0,
        cell_type="cancer",
        outcome="cell death",
        primary_studies=15,
        review_mentions=20,
        claim_type="cytotoxic"
    )
    print(f"Recommendation: {result1.recommendation}")
    print(f"Dose: {result1.dose_context.band.value}")
    print(f"Cell relevance: {result1.cell_context.expected_vdac1_relevance}")
    print(f"Literature tier: {result1.literature_weight.prevalence_tier}")
    for warning in result1.warnings:
        print(warning)
    print()
    
    # Test Case 2: VDAC1 for neuroprotection (INVALID)
    print("Test 2: VDAC1 therapeutic mechanism in neurons")
    print("-" * 60)
    result2 = validate_mechanism_claim(
        mechanism="VDAC1",
        concentration_um=2.0,
        cell_type="neuron",
        outcome="neuroprotection",
        primary_studies=15,
        review_mentions=20,
        claim_type="therapeutic"
    )
    print(f"Recommendation: {result2.recommendation}")
    print(f"Dose: {result2.dose_context.band.value}")
    print(f"Polarity aligned: {result2.polarity_check.aligned}")
    for warning in result2.warnings:
        print(warning)
    print()
    
    # Test Case 3: TRPV1 for pain relief (VALID)
    print("Test 3: TRPV1 therapeutic mechanism")
    print("-" * 60)
    result3 = validate_mechanism_claim(
        mechanism="TRPV1",
        concentration_um=3.0,
        cell_type="neuron",
        outcome="pain relief",
        primary_studies=200,
        review_mentions=85,
        claim_type="therapeutic"
    )
    print(f"Recommendation: {result3.recommendation}")
    print(f"Dose: {result3.dose_context.band.value}")
    print(f"Literature tier: {result3.literature_weight.prevalence_tier}")
    print(f"LWI: {result3.literature_weight.literature_weight_index:.1%}")
    for warning in result3.warnings:
        print(warning)
    print()
    
    print("=" * 60)
    print("Context Gates Framework Ready for Integration")
    print("=" * 60)
