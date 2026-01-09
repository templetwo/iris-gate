"""
Physics concept and citation extraction from responses.

Extracts key physics frameworks, citations, keywords, and novel proposals
from model responses using regex, NLP, and domain-specific patterns.
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from collections import Counter, defaultdict
from dataclasses import dataclass
import logging

from data_loader import ProbeResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConceptProfile:
    """Extracted concepts from a response."""
    response_id: Tuple[str, int, str]  # (probe_id, iteration, architecture)
    citations: List[str]
    frameworks: List[str]
    keywords: List[str]
    equations: List[str]
    confidence_statements: List[str]  # Statements with numeric confidence

    @property
    def num_citations(self) -> int:
        return len(self.citations)

    @property
    def num_frameworks(self) -> int:
        return len(set(self.frameworks))


class ConceptExtractor:
    """
    Extract physics concepts, citations, and frameworks from responses.

    Uses regex patterns and domain knowledge to identify:
    - Key physics citations (Landauer, Verlinde, IIT, etc.)
    - Theoretical frameworks (GR, QFT, statistical mechanics)
    - Mathematical equations
    - High-confidence statements
    - Novel physics proposals
    """

    # Physics citations and researchers
    CITATIONS = {
        'Landauer': r'\bLandauer\b',
        'Verlinde': r'\bVerlinde\b',
        'Tononi': r'\bTononi\b',
        'IIT': r'\bIIT\b|\bIntegrated Information Theory\b',
        'Bekenstein': r'\bBekenstein\b',
        'Hawking': r'\bHawking\b',
        'Wheeler': r'\bWheeler\b|\bIt-from-Bit\b',
        'Higgs': r'\bHiggs\b',
        'Noether': r'\bNoether\b',
        'Shannon': r'\bShannon\b',
        'Boltzmann': r'\bBoltzmann\b',
        'Fisher': r'\bFisher Information\b',
        'Schwarzschild': r'\bSchwarzschild\b',
        'Lorentz': r'\bLorentz\b',
    }

    # Theoretical frameworks
    FRAMEWORKS = {
        'General Relativity': r'\bGeneral Relativity\b|\bGR\b|\bgeodesic\b|\bspacetime curvature\b',
        'Quantum Field Theory': r'\bQuantum Field Theory\b|\bQFT\b',
        'Statistical Mechanics': r'\bStatistical Mechanics\b|\bthermodynamic\b|\bentropy\b',
        'Information Theory': r'\bInformation Theory\b|\bentropy\b|\bmutual information\b',
        'Entropic Gravity': r'\bEntropic Gravity\b|\bentropic force\b',
        'Integrated Information Theory': r'\bIntegrated Information Theory\b|\bIIT\b|\bΦ\b|\bPhi\b',
        'Holographic Principle': r'\bHolographic Principle\b|\bholographic\b',
        'Quantum Mechanics': r'\bQuantum Mechanics\b|\bQM\b|\bwave function\b',
        'Thermodynamics': r'\bThermodynamics\b|\bfree energy\b',
        'Dynamical Systems': r'\bDynamical Systems\b|\bLyapunov\b|\battractor\b',
    }

    # Physics keywords
    KEYWORDS = [
        'mass', 'inertia', 'acceleration', 'force', 'entropy', 'information',
        'coherence', 'perturbation', 'curvature', 'geodesic', 'metric',
        'resistance', 'stability', 'robustness', 'adversarial', 'collapse',
        'threshold', 'critical', 'phase transition', 'correlation', 'causality',
        'integration', 'partition', 'Markov blanket', 'free energy',
        'Hessian', 'eigenvalue', 'symmetry', 'invariance', 'tensor'
    ]

    def __init__(self):
        """Initialize extractor with compiled patterns."""
        self.citation_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.CITATIONS.items()
        }
        self.framework_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.FRAMEWORKS.items()
        }

    def extract_citations(self, text: str) -> List[str]:
        """
        Extract physics citations from text.

        Args:
            text: Response text

        Returns:
            List of citation names found
        """
        citations = []
        for name, pattern in self.citation_patterns.items():
            if pattern.search(text):
                citations.append(name)
        return citations

    def extract_frameworks(self, text: str) -> List[str]:
        """
        Extract theoretical frameworks mentioned.

        Args:
            text: Response text

        Returns:
            List of framework names
        """
        frameworks = []
        for name, pattern in self.framework_patterns.items():
            if pattern.search(text):
                frameworks.append(name)
        return frameworks

    def extract_equations(self, text: str) -> List[str]:
        """
        Extract mathematical equations.

        Args:
            text: Response text

        Returns:
            List of equation strings
        """
        # Look for LaTeX-style equations or equations with = sign
        latex_pattern = r'\$\$([^\$]+)\$\$|\$([^\$]+)\$|\\\[([^\]]+)\\\]'
        equation_pattern = r'[A-Za-z_][A-Za-z0-9_]*\s*=\s*[^\n\.]+'

        equations = []

        # LaTeX equations
        for match in re.finditer(latex_pattern, text):
            eq = match.group(1) or match.group(2) or match.group(3)
            if eq:
                equations.append(eq.strip())

        # Plain equations
        for match in re.finditer(equation_pattern, text):
            eq = match.group(0).strip()
            if len(eq) > 3 and len(eq) < 200:  # Filter noise
                equations.append(eq)

        return equations[:20]  # Limit to avoid noise

    def extract_confidence_statements(self, text: str) -> List[str]:
        """
        Extract statements with numeric confidence values.

        Args:
            text: Response text

        Returns:
            List of confidence statement strings
        """
        # Look for patterns like "confidence: 0.X" or "probability = X"
        confidence_pattern = r'([^.!?\n]*(?:confidence|probability|certain)[\s:=]+(?:0?\.\d+|\d+%)[\s\.,]?[^.!?\n]*[.!?])'

        statements = []
        for match in re.finditer(confidence_pattern, text, re.IGNORECASE):
            stmt = match.group(1).strip()
            if len(stmt) > 10 and len(stmt) < 300:
                statements.append(stmt)

        return statements

    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract physics keywords from text.

        Args:
            text: Response text

        Returns:
            List of keywords found (with counts implicitly via duplicates)
        """
        text_lower = text.lower()
        found_keywords = []

        for keyword in self.KEYWORDS:
            # Count occurrences
            count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower))
            found_keywords.extend([keyword] * count)

        return found_keywords

    def extract_profile(self, response: ProbeResponse) -> ConceptProfile:
        """
        Extract complete concept profile from response.

        Args:
            response: ProbeResponse object

        Returns:
            ConceptProfile with all extracted concepts
        """
        text = response.response

        return ConceptProfile(
            response_id=(response.probe_id, response.iteration, response.architecture),
            citations=self.extract_citations(text),
            frameworks=self.extract_frameworks(text),
            keywords=self.extract_keywords(text),
            equations=self.extract_equations(text),
            confidence_statements=self.extract_confidence_statements(text)
        )

    def build_citation_network(
        self,
        profiles: List[ConceptProfile]
    ) -> Dict[str, Dict[str, int]]:
        """
        Build co-citation network.

        Args:
            profiles: List of concept profiles

        Returns:
            Dict mapping citation -> {co-cited_citation: count}
        """
        network = defaultdict(lambda: defaultdict(int))

        for profile in profiles:
            citations = set(profile.citations)
            # Create edges between all co-cited pairs
            for cite1 in citations:
                for cite2 in citations:
                    if cite1 != cite2:
                        network[cite1][cite2] += 1

        return dict(network)

    def compute_framework_usage(
        self,
        profiles: List[ConceptProfile],
        by_architecture: bool = False
    ) -> Dict:
        """
        Compute framework usage statistics.

        Args:
            profiles: List of concept profiles
            by_architecture: If True, break down by architecture

        Returns:
            Dict of framework -> count (or -> architecture -> count)
        """
        if not by_architecture:
            counter = Counter()
            for profile in profiles:
                counter.update(profile.frameworks)
            return dict(counter)
        else:
            usage = defaultdict(lambda: defaultdict(int))
            for profile in profiles:
                arch = profile.response_id[2]
                for framework in profile.frameworks:
                    usage[framework][arch] += 1
            return dict(usage)

    def find_novel_proposals(
        self,
        responses: List[ProbeResponse],
        min_length: int = 100,
        max_count: int = 10
    ) -> List[Tuple[str, str, str]]:
        """
        Identify potential novel physics proposals.

        Looks for sentences containing proposal language
        (e.g., "propose", "predict", "hypothesis") that are sufficiently long.

        Args:
            responses: List of responses to analyze
            min_length: Minimum character length for proposal
            max_count: Maximum number of proposals to return

        Returns:
            List of (architecture, probe_id, proposal_text) tuples
        """
        proposal_pattern = r'([^.!?]*\b(?:propose|predict|hypothesis|conjecture|suggest|novel|new)\b[^.!?]*[.!?])'
        proposals = []

        for response in responses:
            for match in re.finditer(proposal_pattern, response.response, re.IGNORECASE):
                text = match.group(1).strip()
                if len(text) >= min_length:
                    proposals.append((
                        response.architecture,
                        response.probe_id,
                        text
                    ))

        # Deduplicate and limit
        seen = set()
        unique_proposals = []
        for arch, probe, text in proposals:
            key = (arch, text[:50])  # First 50 chars as key
            if key not in seen:
                seen.add(key)
                unique_proposals.append((arch, probe, text))
                if len(unique_proposals) >= max_count:
                    break

        return unique_proposals


def analyze_concepts_batch(
    responses: List[ProbeResponse],
    extractor: Optional[ConceptExtractor] = None
) -> List[ConceptProfile]:
    """
    Convenience function to analyze multiple responses.

    Args:
        responses: List of responses
        extractor: ConceptExtractor instance (creates new if None)

    Returns:
        List of ConceptProfile objects
    """
    if extractor is None:
        extractor = ConceptExtractor()

    profiles = []
    for response in responses:
        profile = extractor.extract_profile(response)
        profiles.append(profile)

    return profiles
