#!/usr/bin/env python3
"""
IRIS Gate Verifier - Real-time claim verification via Perplexity

Uses Perplexity's real-time search to verify claims from IRIS convergence,
particularly TYPE 2 (VERIFY zone) responses.

Architecture:
- Extract factual claims from S4 responses
- Query Perplexity for real-time literature validation
- Return structured verification: SUPPORTED / PARTIALLY_SUPPORTED / NOVEL / CONTRADICTED
- Cite sources with dates for transparency
"""

import os
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from pathlib import Path


@dataclass
class Claim:
    """A factual claim extracted from IRIS response"""
    text: str
    category: str  # mechanism, prediction, relationship, fact
    confidence: str  # explicit, implicit
    line_number: Optional[int] = None


@dataclass
class VerificationResult:
    """Result of verifying a claim against real-time literature"""
    claim: str
    status: str  # SUPPORTED, PARTIALLY_SUPPORTED, NOVEL, CONTRADICTED
    confidence: str  # HIGH, MODERATE, LOW
    sources: List[Dict]  # [{title, url, date, snippet}, ...]
    reasoning: str
    perplexity_response: str


class PerplexityAdapter:
    """
    Adapter for Perplexity API calls.

    Uses Perplexity's sonar models with real-time web search.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment")

        self.base_url = "https://api.perplexity.ai"
        self.model = "sonar"  # Real-time search model

    def search(self, query: str, return_citations: bool = True) -> Dict:
        """
        Query Perplexity with real-time search.

        Args:
            query: Search query / claim to verify
            return_citations: Include source citations

        Returns:
            Dict with response text and citations
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a scientific literature verification assistant. "
                        "Evaluate the following claim against current research. "
                        "Provide:\n"
                        "1. Status: SUPPORTED / PARTIALLY_SUPPORTED / NOVEL / CONTRADICTED\n"
                        "2. Confidence: HIGH / MODERATE / LOW\n"
                        "3. Evidence summary with specific papers and dates\n"
                        "4. Key caveats or nuances\n\n"
                        "Be precise about what is established vs exploratory."
                    )
                },
                {
                    "role": "user",
                    "content": f"Verify this claim: {query}"
                }
            ],
            "return_citations": return_citations,
            "return_related_questions": False,
            "search_recency_filter": "month",  # Prioritize recent papers
            "temperature": 0.2  # Low temperature for factual verification
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        return {
            "text": data["choices"][0]["message"]["content"],
            "citations": data.get("citations", []),
            "model": data["model"],
            "usage": data.get("usage", {})
        }


class ClaimExtractor:
    """
    Extract factual claims from IRIS S4 responses.

    Focuses on:
    - Mechanistic statements (X causes Y)
    - Quantitative predictions (50-80% reduction)
    - Relationships (gap junctions enable coupling)
    - Facts (CBD shows biphasic response)
    """

    # Patterns for extracting claims
    MECHANISM_PATTERNS = [
        r"(?:causes?|leads? to|results? in|induces?|triggers?|activates?|inhibits?|blocks?|disrupts?)\s+([^.;]+)",
        r"([^.;]+)\s+(?:by|through|via)\s+([^.;]+)",
    ]

    QUANTITATIVE_PATTERNS = [
        r"(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?%)\s+([^.;]+)",
        r"([^.;]+)\s+(?:by|to)\s+(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?%)",
    ]

    CONFIDENCE_MARKERS = {
        "high": ["established", "demonstrated", "confirmed", "validated", "proven", "well-known"],
        "medium": ["suggests", "indicates", "appears", "seems", "likely", "probable"],
        "low": ["might", "could", "possibly", "speculatively", "hypothetically", "unclear"]
    }

    def extract_claims(self, text: str) -> List[Claim]:
        """
        Extract factual claims from text.

        Args:
            text: S4 response text

        Returns:
            List of Claim objects
        """
        claims = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if len(line) < 20:  # Skip very short lines
                continue

            # Check for quantitative claims
            for pattern in self.QUANTITATIVE_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    claim_text = line
                    confidence = self._detect_confidence(line)
                    claims.append(Claim(
                        text=claim_text,
                        category="quantitative",
                        confidence=confidence,
                        line_number=line_num
                    ))

            # Check for mechanistic claims
            for pattern in self.MECHANISM_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    claim_text = line
                    confidence = self._detect_confidence(line)
                    claims.append(Claim(
                        text=claim_text,
                        category="mechanism",
                        confidence=confidence,
                        line_number=line_num
                    ))

        # Deduplicate claims
        unique_claims = []
        seen_texts = set()
        for claim in claims:
            if claim.text not in seen_texts:
                unique_claims.append(claim)
                seen_texts.add(claim.text)

        return unique_claims[:10]  # Limit to top 10 claims for efficiency

    def _detect_confidence(self, text: str) -> str:
        """Detect confidence level from language markers"""
        text_lower = text.lower()

        for level, markers in self.CONFIDENCE_MARKERS.items():
            if any(marker in text_lower for marker in markers):
                return level

        return "medium"  # Default


class IRISVerifier:
    """
    Main verifier class - orchestrates claim extraction and verification.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.perplexity = PerplexityAdapter(api_key)
        self.extractor = ClaimExtractor()

    def verify_response(self, response_text: str, epistemic_type: Optional[int] = None) -> Dict:
        """
        Verify IRIS response against real-time literature.

        Args:
            response_text: S4 response text
            epistemic_type: Epistemic type (0-3), if known

        Returns:
            Dict with verification results
        """
        # Extract claims
        claims = self.extractor.extract_claims(response_text)

        if not claims:
            return {
                "status": "NO_CLAIMS",
                "message": "No extractable factual claims found in response",
                "epistemic_type": epistemic_type,
                "timestamp": datetime.utcnow().isoformat()
            }

        # Verify each claim
        results = []
        for claim in claims:
            try:
                verification = self._verify_claim(claim)
                results.append(verification)
            except Exception as e:
                results.append(VerificationResult(
                    claim=claim.text,
                    status="ERROR",
                    confidence="LOW",
                    sources=[],
                    reasoning=f"Verification failed: {str(e)}",
                    perplexity_response=""
                ))

        # Compute overall verification summary
        summary = self._compute_summary(results)

        return {
            "status": "VERIFIED",
            "epistemic_type": epistemic_type,
            "total_claims": len(claims),
            "results": [asdict(r) for r in results],
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _verify_claim(self, claim: Claim) -> VerificationResult:
        """Verify a single claim via Perplexity"""
        # Query Perplexity
        query_result = self.perplexity.search(claim.text)
        response_text = query_result["text"]
        citations = query_result.get("citations", [])

        # Parse response to extract status and confidence
        status = self._extract_status(response_text)
        confidence = self._extract_confidence(response_text)

        # Format sources
        sources = self._format_sources(citations)

        return VerificationResult(
            claim=claim.text,
            status=status,
            confidence=confidence,
            sources=sources,
            reasoning=response_text,
            perplexity_response=response_text
        )

    def _extract_status(self, text: str) -> str:
        """Extract verification status from Perplexity response"""
        text_upper = text.upper()

        if "SUPPORTED" in text_upper and "PARTIALLY" not in text_upper:
            return "SUPPORTED"
        elif "PARTIALLY" in text_upper or "PARTIAL" in text_upper:
            return "PARTIALLY_SUPPORTED"
        elif "NOVEL" in text_upper or "NO DIRECT" in text_upper:
            return "NOVEL"
        elif "CONTRADICTED" in text_upper or "INCONSISTENT" in text_upper:
            return "CONTRADICTED"
        else:
            return "UNCLEAR"

    def _extract_confidence(self, text: str) -> str:
        """Extract confidence level from Perplexity response"""
        text_upper = text.upper()

        if "HIGH" in text_upper:
            return "HIGH"
        elif "LOW" in text_upper:
            return "LOW"
        else:
            return "MODERATE"

    def _format_sources(self, citations: List) -> List[Dict]:
        """Format citation data into source dicts"""
        sources = []
        for citation in citations[:5]:  # Top 5 sources
            sources.append({
                "title": citation.get("title", "Unknown"),
                "url": citation.get("url", ""),
                "snippet": citation.get("snippet", "")[:200]  # Truncate
            })
        return sources

    def _compute_summary(self, results: List[VerificationResult]) -> Dict:
        """Compute overall verification summary"""
        if not results:
            return {"overall_status": "NO_DATA"}

        status_counts = {}
        confidence_counts = {}

        for result in results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1
            confidence_counts[result.confidence] = confidence_counts.get(result.confidence, 0) + 1

        # Determine overall status
        if status_counts.get("SUPPORTED", 0) >= len(results) * 0.7:
            overall_status = "MOSTLY_SUPPORTED"
        elif status_counts.get("NOVEL", 0) >= len(results) * 0.5:
            overall_status = "EXPLORATORY"
        elif status_counts.get("CONTRADICTED", 0) > 0:
            overall_status = "CONFLICTS_DETECTED"
        else:
            overall_status = "MIXED"

        return {
            "overall_status": overall_status,
            "status_distribution": status_counts,
            "confidence_distribution": confidence_counts,
            "high_confidence_supported": status_counts.get("SUPPORTED", 0),
            "novel_claims": status_counts.get("NOVEL", 0),
            "contradictions": status_counts.get("CONTRADICTED", 0)
        }


def verify_scroll(scroll_path: str, api_key: Optional[str] = None) -> Dict:
    """
    Verify an S4 scroll file.

    Args:
        scroll_path: Path to S4 markdown scroll
        api_key: Optional Perplexity API key

    Returns:
        Verification results dict
    """
    verifier = IRISVerifier(api_key)

    # Read scroll
    scroll_text = Path(scroll_path).read_text()

    # Extract epistemic type if present
    epistemic_type = None
    match = re.search(r"\[TYPE (\d+):", scroll_text)
    if match:
        epistemic_type = int(match.group(1))

    # Extract raw response section
    parts = scroll_text.split('---')
    if len(parts) >= 3:
        response_text = parts[1].strip()
    else:
        response_text = scroll_text

    return verifier.verify_response(response_text, epistemic_type)


def verify_session(session_path: str, api_key: Optional[str] = None) -> Dict:
    """
    Verify all TYPE 2 responses in a session.

    Args:
        session_path: Path to session JSON file
        api_key: Optional Perplexity API key

    Returns:
        Session verification results
    """
    verifier = IRISVerifier(api_key)

    # Load session
    with open(session_path, 'r') as f:
        session_data = json.load(f)

    session_results = {
        "session_file": session_path,
        "timestamp": datetime.utcnow().isoformat(),
        "mirrors": {}
    }

    # Verify TYPE 2 responses
    for mirror_id, turns in session_data.get("mirrors", {}).items():
        mirror_verifications = []

        for turn in turns:
            epistemic = turn.get("epistemic", {})
            if epistemic.get("type") == 2:  # TYPE 2 - VERIFY zone
                response_text = turn.get("raw_response", "")
                verification = verifier.verify_response(response_text, epistemic_type=2)
                verification["chamber"] = turn.get("condition", "Unknown")
                mirror_verifications.append(verification)

        if mirror_verifications:
            session_results["mirrors"][mirror_id] = mirror_verifications

    return session_results


if __name__ == "__main__":
    # Test with a sample claim
    print("🔬 IRIS Verifier - Real-time Claim Verification\n")

    verifier = IRISVerifier()

    test_claim = "Gap junction blockers like carbenoxolone reduce intercellular coupling by 50-80% in planarian cells."

    print(f"Testing with claim:\n  \"{test_claim}\"\n")
    print("Querying Perplexity...")

    result = verifier.verify_response(test_claim)

    print("\n" + "="*80)
    print("VERIFICATION RESULT")
    print("="*80)
    print(json.dumps(result, indent=2))
