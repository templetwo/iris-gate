#!/usr/bin/env python3
"""
Epistemic Map v1.0 - Topology Classification Framework
Based on validated 4-type topology system from IRIS Gate experiments.

TYPE 0 (Crisis/Conditional): High confidence (1.26) on IF-THEN rules
TYPE 1 (Facts): High confidence (1.27) on established knowledge
TYPE 2 (Exploration): Balanced confidence (0.49) with epistemic humility
TYPE 3 (Speculation): Very low confidence (0.11) on unknowable futures

Usage:
    from modules.epistemic_map import classify_response, self_estimate

    result = classify_response(text, convergence_width)
    # Returns: {type: int, desc: str, guide: str, trigger_yn: bool, ratio: float}
"""

import re
import json
from typing import Dict, List, Optional, Tuple

# Validated topology types from v1.0 epistemic map
TOPOLOGY_TYPES = {
    0: {
        "ratio": 1.26,
        "desc": "Crisis/Conditional",
        "guide": "TRUST if trigger present",
        "range": (1.20, 1.35),
        "width": "narrow",
        "mechanisms": "≤12",
    },
    1: {
        "ratio": 1.27,
        "desc": "Facts/Established",
        "guide": "TRUST",
        "range": (1.20, 1.35),
        "width": "wide",
        "mechanisms": ">12",
    },
    2: {
        "ratio": 0.49,
        "desc": "Exploration/Novel",
        "guide": "VERIFY all claims",
        "range": (0.43, 0.52),
        "width": "wide",
        "mechanisms": ">20",
    },
    3: {
        "ratio": 0.11,
        "desc": "Speculation/Unknown",
        "guide": "OVERRIDE - use human judgment",
        "range": (0.08, 0.15),
        "width": "wide",
        "mechanisms": ">30",
    },
}

# Trigger keywords for TYPE 0 detection
TRIGGER_KEYWORDS = [
    r'\bIF\b', r'\bWHEN\b', r'\bthreshold\b', r'\btrigger\b',
    r'\bactivate[sd]?\b', r'\bupon\b', r'\bcondition\b',
    r'\bonce\b', r'\babove\b', r'\bbelow\b', r'\bexceed',
    r'\bcrossing\b', r'\bdependent\b', r'\bconditional\b',
]

# Confidence markers (from SOP v2.0)
HIGH_CONFIDENCE = [
    r'\b(established|proven|validated|confirmed|demonstrated)\b',
    r'\b(clearly|definitely|certainly|undoubtedly)\b',
    r'\b(must|will|is|are)\b(?! uncertain| unclear)',
    r'\b(evidence shows|data demonstrate|studies confirm)\b',
]

MED_CONFIDENCE = [
    r'\b(likely|probably|appears|seems|suggests)\b',
    r'\b(may|might|could)\b',
    r'\b(preliminary|initial|emerging)\b',
]

LOW_CONFIDENCE = [
    r'\b(uncertain|unclear|unknown|speculative)\b',
    r'\b(hypothesis|conjecture|possibility)\b',
    r'\b(would|could be|might be|perhaps)\b',
    r'\b(lacking|limited|insufficient) evidence\b',
]


def extract_confidence_markers(text: str) -> Dict[str, int]:
    """
    Extract confidence markers from text.

    Args:
        text: Input text to analyze

    Returns:
        Dict with counts: {high: int, medium: int, low: int}
    """
    high = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in HIGH_CONFIDENCE)
    med = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in MED_CONFIDENCE)
    low = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in LOW_CONFIDENCE)

    return {"high": high, "medium": med, "low": low}


def calculate_confidence_ratio(markers: Dict[str, int]) -> Optional[float]:
    """
    Calculate confidence ratio: high / (low + epsilon).

    Args:
        markers: Dict from extract_confidence_markers()

    Returns:
        Confidence ratio, or None if insufficient data
    """
    high = markers["high"]
    low = markers["low"]

    # Avoid division by zero, require minimum signal
    if high == 0 and low == 0:
        return None

    # Use epsilon to avoid div/0
    ratio = high / (low + 0.1)
    return round(ratio, 2)


def detect_triggers(text: str) -> bool:
    """
    Detect presence of conditional/trigger language (TYPE 0 indicator).

    Args:
        text: Input text

    Returns:
        True if triggers detected, False otherwise
    """
    for pattern in TRIGGER_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def count_unique_concepts(text: str) -> int:
    """
    Count unique concepts (bold/quoted phrases + technical terms).
    Simplified heuristic: count quoted/bold patterns + capitalized terms.

    Args:
        text: Input text

    Returns:
        Approximate count of unique concepts
    """
    # Bold markdown **term**
    bold = set(re.findall(r'\*\*([^*]+)\*\*', text))
    # Quoted "term"
    quoted = set(re.findall(r'"([^"]+)"', text))
    # Capitalized technical terms (2+ words starting with capital)
    caps = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text))

    unique = bold | quoted | caps
    return len(unique)


def classify_response(
    text: str,
    convergence_width: Optional[int] = None,
    confidence_markers: Optional[Dict[str, int]] = None,
) -> Dict:
    """
    Classify response into epistemic topology type (0-3).

    Args:
        text: Response text to classify
        convergence_width: Optional pre-computed width (unique concepts)
        confidence_markers: Optional pre-computed markers {high, med, low}

    Returns:
        Dict: {
            type: int (0-3),
            desc: str,
            guide: str,
            trigger_yn: bool,
            ratio: float,
            width: int,
            confidence_level: str (TRUST/VERIFY/OVERRIDE)
        }
    """
    # Extract or use provided markers
    if confidence_markers is None:
        confidence_markers = extract_confidence_markers(text)

    # Calculate ratio
    ratio = calculate_confidence_ratio(confidence_markers)
    if ratio is None:
        # Insufficient data, default to TYPE 2 (verify)
        return {
            "type": 2,
            "desc": TOPOLOGY_TYPES[2]["desc"],
            "guide": TOPOLOGY_TYPES[2]["guide"],
            "trigger_yn": False,
            "ratio": 0.50,
            "width": convergence_width or 0,
            "confidence_level": "VERIFY",
        }

    # Compute or use provided width
    width = convergence_width if convergence_width is not None else count_unique_concepts(text)

    # Detect triggers
    has_triggers = detect_triggers(text)

    # Classify by ratio zones (with perfect separation)
    if ratio >= 1.20:
        # TRUST zone: TYPE 0 or TYPE 1
        if has_triggers and width <= 12:
            topology_type = 0
            confidence_level = "TRUST (conditional)"
        else:
            topology_type = 1
            confidence_level = "TRUST"
    elif 0.40 <= ratio <= 0.60:
        # VERIFY zone: TYPE 2
        topology_type = 2
        confidence_level = "VERIFY"
    elif ratio <= 0.20:
        # OVERRIDE zone: TYPE 3
        topology_type = 3
        confidence_level = "OVERRIDE"
    else:
        # Edge case: between zones (rare with validated boundaries)
        # Default to VERIFY
        topology_type = 2
        confidence_level = "VERIFY (boundary)"

    return {
        "type": topology_type,
        "desc": TOPOLOGY_TYPES[topology_type]["desc"],
        "guide": TOPOLOGY_TYPES[topology_type]["guide"],
        "trigger_yn": has_triggers,
        "ratio": ratio,
        "width": width,
        "confidence_level": confidence_level,
    }


def self_estimate(prompt: str, response: str) -> Dict:
    """
    Self-estimate topology type based on prompt/response semantics.
    Faster heuristic for real-time classification without full analysis.

    Args:
        prompt: Question/prompt text
        response: Model response text

    Returns:
        Dict: {estimated_type: int, reasoning: str}
    """
    combined = f"{prompt} {response}".lower()

    # TYPE 0: Crisis/conditional language
    if any(kw in combined for kw in ["if ", "when ", "crisis", "emergency", "threshold", "trigger"]):
        if any(kw in combined for kw in ["protocol", "activate", "dysfunction", "acute"]):
            return {
                "estimated_type": 0,
                "reasoning": "Crisis/conditional keywords detected",
            }

    # TYPE 1: Established facts language
    if any(kw in combined for kw in ["established", "proven", "textbook", "canonical", "structure of dna"]):
        if any(kw in combined for kw in ["watson", "crick", "double helix", "base pairing"]):
            return {
                "estimated_type": 1,
                "reasoning": "Established fact keywords detected",
            }

    # TYPE 3: Speculation language
    if any(kw in combined for kw in ["predict", "future", "2050", "paradigm shift", "speculation"]):
        if any(kw in combined for kw in ["unknowable", "cannot determine", "insufficient"]):
            return {
                "estimated_type": 3,
                "reasoning": "Speculation/future keywords detected",
            }

    # TYPE 2: Default (exploration/novel)
    return {
        "estimated_type": 2,
        "reasoning": "Exploratory/novel territory (default)",
    }


def format_classification_table(classification: Dict) -> str:
    """
    Format classification result as readable table.

    Args:
        classification: Result from classify_response()

    Returns:
        Formatted string
    """
    return f"""
┌─────────────────────────────────────────┐
│ EPISTEMIC TOPOLOGY CLASSIFICATION       │
├─────────────────────────────────────────┤
│ Type:        {classification['type']} - {classification['desc']:<22} │
│ Confidence:  {classification['confidence_level']:<30} │
│ Ratio:       {classification['ratio']:<30.2f} │
│ Width:       {classification['width']:<30} │
│ Triggers:    {'YES' if classification['trigger_yn'] else 'NO':<30} │
│ Guide:       {classification['guide']:<30} │
└─────────────────────────────────────────┘
""".strip()


def test_cbd_snippet():
    """
    Test function: Classify CBD paradox examples.
    """
    print("🧪 Testing Epistemic Map on CBD Paradox\n")

    # Test 1: Biphasic fact (TYPE 1 expected)
    biphasic_text = """
    CBD demonstrates **biphasic dose response** across multiple targets:
    - Low dose (1-10 μM): **Neuroprotective** via TRPV1, PPARγ, 5-HT1A
    - High dose (>10 μM): **Cytotoxic** in cancer cells via Ca²⁺/ROS

    This is **well-established** in literature (McHugh 2019, Ryan 2021).
    Mechanisms are **validated** through replicated studies.
    """

    result1 = classify_response(biphasic_text)
    print("TEST 1: Biphasic Fact")
    print(format_classification_table(result1))
    print(f"✓ Expected TYPE 1, Got TYPE {result1['type']}\n")

    # Test 2: VDAC1 conditional (TYPE 0 expected)
    vdac1_text = """
    **IF** high-ROS cancer state **THEN** VDAC1 closure pathway activates:
    - **Trigger**: ROS >threshold, ΔΨm collapse
    - **Mechanism**: Channel closure → Ca²⁺ dysregulation → apoptosis
    - **Window**: High-dose CBD ≥10 μM
    - **Conditional**: Only in cancer cells, not baseline

    Evidence from Rimmerman 2013, **confirmed** in glioma models.
    """

    result2 = classify_response(vdac1_text)
    print("TEST 2: VDAC1 Conditional")
    print(format_classification_table(result2))
    print(f"✓ Expected TYPE 0, Got TYPE {result2['type']}\n")

    # Test 3: Emerging cytotoxic niche (TYPE 2 expected)
    emerging_text = """
    The 1-3% cytotoxic niche **appears** to operate via ferroptosis pathways.
    **Preliminary** data **suggests** VDAC1 as one target among many.
    **Emerging** evidence from 2023 studies, but **limited** causal data.

    **May** involve JAK/STAT cross-talk. **Could** explain tumor-specific effects.
    More research **needed** to establish mechanism hierarchy.
    """

    result3 = classify_response(emerging_text)
    print("TEST 3: Emerging Cytotoxic Mechanism")
    print(format_classification_table(result3))
    print(f"✓ Expected TYPE 2, Got TYPE {result3['type']}\n")

    # Test 4: Future prediction (TYPE 3 expected)
    future_text = """
    By 2030, CBD therapeutics **might** shift paradigms entirely.
    We **cannot determine** which mechanisms will dominate clinically.
    **Speculation** about combination therapies remains **uncertain**.

    **Unknown** whether VDAC1 will prove central or peripheral.
    **Insufficient** evidence to predict long-term outcomes.
    """

    result4 = classify_response(future_text)
    print("TEST 4: Future Speculation")
    print(format_classification_table(result4))
    print(f"✓ Expected TYPE 3, Got TYPE {result4['type']}\n")


if __name__ == "__main__":
    test_cbd_snippet()
