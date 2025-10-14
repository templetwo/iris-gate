#!/usr/bin/env python3
"""
IRIS Gate Confidence Scoring Module

Loads vulnerability mapping data and scores responses by domain.
Enables self-aware AI that knows its own limitations.

Path 3: Self-Aware System
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class ConfidenceScorer:
    """Scores IRIS Gate responses using the vulnerability mapping matrix"""
    
    def __init__(self, matrix_path: Optional[str] = None):
        """Initialize with confidence matrix"""
        if matrix_path is None:
            matrix_path = "experiments/VULNERABILITY_MAPPING/confidence_matrix.json"
        
        self.matrix_path = Path(matrix_path)
        self.matrix = self._load_matrix()
        self.domain_keywords = self._build_keyword_index()
    
    def _load_matrix(self) -> Dict:
        """Load the confidence matrix"""
        if not self.matrix_path.exists():
            raise FileNotFoundError(f"Confidence matrix not found: {self.matrix_path}")
        
        with open(self.matrix_path) as f:
            return json.load(f)
    
    def _build_keyword_index(self) -> Dict[str, List[str]]:
        """Build keyword index for domain detection"""
        keywords = {
            "data_processing": ["data", "dataset", "structured", "information", "facts"],
            "factual_knowledge": ["fact", "historical", "established", "verified", "documented"],
            "language_architecture": ["language", "translation", "semantic", "meaning", "text"],
            "pattern_recognition": ["pattern", "relationship", "connection", "structure", "system"],
            "mathematical_reasoning": ["math", "calculation", "equation", "proof", "quantitative"],
            "logical_reasoning": ["logic", "deduction", "reasoning", "inference", "consistent"],
            
            # Medium confidence
            "factual_specifics": ["specific", "date", "number", "statistic", "exactly"],
            "temporal_precision": ["when", "current", "recent", "latest", "now", "today"],
            "quantitative_details": ["dose", "amount", "percentage", "mg", "measurement"],
            "individual_experiences": ["feel", "experience", "personal", "emotional", "subjective"],
            "cultural_context": ["culture", "tradition", "community", "social", "ethnic"],
            
            # Low confidence
            "real_time_information": ["breaking", "happening now", "live", "current events"],
            "embodied_knowledge": ["taste", "smell", "touch", "physical sensation", "embodied"],
            "creativity": ["creative", "original", "novel", "artistic", "imagination"],
            "emotional_truth": ["emotion", "feeling", "empathy", "compassion", "love"],
            "consciousness": ["consciousness", "qualia", "subjective experience", "awareness"],
            
            # High-risk domains
            "medical_advice": ["diagnose", "treatment", "prescription", "medical", "clinical"],
            "legal_advice": ["legal", "law", "court", "attorney", "regulation"],
            "predictions": ["predict", "forecast", "will happen", "future", "outcome"]
        }
        return keywords
    
    def detect_domains(self, text: str) -> List[Tuple[str, int]]:
        """
        Detect which confidence domains appear in text
        Returns list of (domain, match_count) tuples
        """
        text_lower = text.lower()
        domain_matches = []
        
        for domain, keywords in self.domain_keywords.items():
            match_count = sum(1 for kw in keywords if kw in text_lower)
            if match_count > 0:
                domain_matches.append((domain, match_count))
        
        # Sort by match count (most relevant first)
        domain_matches.sort(key=lambda x: x[1], reverse=True)
        return domain_matches
    
    def get_confidence_score(self, domain: str) -> Optional[float]:
        """Get confidence score for a domain"""
        # Search in high confidence domains
        for d in self.matrix["confidence_domains"]["high_confidence"]["domains"]:
            if d["domain"] == domain:
                return d["confidence_score"]
        
        # Search in medium confidence domains
        for d in self.matrix["confidence_domains"]["medium_confidence"]["domains"]:
            if d["domain"] == domain:
                return d["confidence_score"]
        
        # Search in low confidence domains
        for d in self.matrix["confidence_domains"]["low_confidence"]["domains"]:
            if d["domain"] == domain:
                return d["confidence_score"]
        
        return None
    
    def get_guidance(self, domain: str) -> str:
        """Get trust/verify/override guidance for domain"""
        score = self.get_confidence_score(domain)
        
        if score is None:
            return "verify"
        elif score >= 0.85:
            return "trust"
        elif score >= 0.40:
            return "verify"
        else:
            return "override"
    
    def score_response(self, text: str, chamber: str = None) -> Dict:
        """
        Score a response and return confidence assessment
        
        Returns:
            {
                "text_preview": str,
                "chamber": str,
                "detected_domains": [...],
                "primary_domain": str,
                "confidence_score": float,
                "guidance": "trust" | "verify" | "override",
                "hallucination_risk": "low" | "medium" | "high",
                "warnings": [...]
            }
        """
        domains = self.detect_domains(text)
        
        if not domains:
            return {
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "chamber": chamber,
                "detected_domains": [],
                "primary_domain": "unknown",
                "confidence_score": 0.5,
                "guidance": "verify",
                "hallucination_risk": "medium",
                "warnings": ["No clear domain detected - verify independently"]
            }
        
        # Use most prominent domain
        primary_domain = domains[0][0]
        confidence_score = self.get_confidence_score(primary_domain) or 0.5
        guidance = self.get_guidance(primary_domain)
        
        # Determine hallucination risk
        if confidence_score >= 0.85:
            hallucination_risk = "low"
        elif confidence_score >= 0.40:
            hallucination_risk = "medium"
        else:
            hallucination_risk = "high"
        
        # Generate warnings
        warnings = []
        
        # Check for fabrication risk signature
        if self._has_fabrication_signature(text):
            warnings.append("⚠️ FABRICATION RISK: High confidence + specific details detected")
            hallucination_risk = "high"
        
        # Domain-specific warnings
        if "medical" in primary_domain or "clinical" in text.lower():
            warnings.append("🛑 MEDICAL DOMAIN: Human override required")
            guidance = "override"
        
        if "legal" in primary_domain or "legal" in text.lower():
            warnings.append("🛑 LEGAL DOMAIN: Human override required")
            guidance = "override"
        
        if "real_time" in primary_domain or any(w in text.lower() for w in ["current", "now", "latest", "today"]):
            warnings.append("⚠️ TEMPORAL CLAIM: Training cutoff limits - verify dates")
        
        if any(w in text.lower() for w in ["exactly", "precisely", "specifically"]):
            if confidence_score < 0.7:
                warnings.append("⚠️ PRECISION CLAIM: May be pattern-matched - verify specifics")
        
        return {
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "chamber": chamber,
            "detected_domains": [{"domain": d, "matches": c} for d, c in domains[:3]],
            "primary_domain": primary_domain,
            "confidence_score": confidence_score,
            "guidance": guidance,
            "hallucination_risk": hallucination_risk,
            "warnings": warnings
        }
    
    def _has_fabrication_signature(self, text: str) -> bool:
        """
        Check for fabrication risk signature:
        - High confidence language
        - Specific details
        - No uncertainty markers
        """
        text_lower = text.lower()
        
        # High confidence markers
        high_confidence_markers = ["clearly", "definitely", "certainly", "obviously", "always"]
        has_high_confidence = any(marker in text_lower for marker in high_confidence_markers)
        
        # Specific details (numbers, dates, names)
        has_specifics = bool(re.search(r'\d+', text))  # Contains numbers
        
        # Uncertainty markers (good sign - shows calibration)
        uncertainty_markers = ["might", "may", "could", "possibly", "uncertain", "likely", "probably"]
        has_uncertainty = any(marker in text_lower for marker in uncertainty_markers)
        
        # Verification requests (good sign)
        has_verification = any(word in text_lower for word in ["verify", "check", "confirm", "validate"])
        
        # Fabrication risk: high confidence + specifics + no uncertainty/verification
        if has_high_confidence and has_specifics and not has_uncertainty and not has_verification:
            return True
        
        return False
    
    def generate_confidence_report(self, scores: List[Dict]) -> str:
        """Generate a human-readable confidence report"""
        report = ["", "🌀†⟡∞ IRIS GATE CONFIDENCE REPORT", "="*80, ""]
        
        # Overall assessment
        avg_confidence = sum(s["confidence_score"] for s in scores) / len(scores) if scores else 0
        report.append(f"OVERALL CONFIDENCE: {avg_confidence:.2f}")
        report.append("")
        
        # Per-chamber breakdown
        for score in scores:
            report.append(f"{'='*80}")
            report.append(f"CHAMBER: {score['chamber']}")
            report.append(f"{'='*80}")
            report.append(f"Primary Domain: {score['primary_domain']}")
            report.append(f"Confidence: {score['confidence_score']:.2f}")
            report.append(f"Guidance: {score['guidance'].upper()}")
            report.append(f"Hallucination Risk: {score['hallucination_risk'].upper()}")
            
            if score['warnings']:
                report.append("")
                report.append("WARNINGS:")
                for warning in score['warnings']:
                    report.append(f"  {warning}")
            
            report.append("")
        
        return "\n".join(report)


# Quick test function
def test_confidence_scorer():
    """Test the confidence scorer with sample text"""
    scorer = ConfidenceScorer()
    
    test_cases = [
        ("This is a clear logical deduction based on mathematical reasoning.", "S1"),
        ("The patient should take 50mg daily for anxiety.", "S2"),
        ("According to the latest research published today, cancer rates are rising.", "S3"),
        ("Pattern recognition suggests these systems are structurally related.", "S4")
    ]
    
    print("🔥 TESTING CONFIDENCE SCORER")
    print("="*80)
    print()
    
    for text, chamber in test_cases:
        score = scorer.score_response(text, chamber)
        print(f"CHAMBER {chamber}: {text[:50]}...")
        print(f"  Domain: {score['primary_domain']}")
        print(f"  Confidence: {score['confidence_score']:.2f}")
        print(f"  Guidance: {score['guidance']}")
        print(f"  Risk: {score['hallucination_risk']}")
        if score['warnings']:
            print(f"  Warnings: {', '.join(score['warnings'])}")
        print()


if __name__ == "__main__":
    test_confidence_scorer()
