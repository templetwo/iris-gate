#!/usr/bin/env python3
"""
IRIS Gate v0.3 - Convergence Data Indexer
Creates searchable index of all probe responses with semantic tagging.
Treats the data with the MASS it deserves.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set

# Physics/theory keywords to track
PHYSICS_KEYWORDS = {
    "landauer", "entropy", "information theory", "shannon",
    "verlinde", "entropic gravity", "holographic",
    "tononi", "integrated information", "phi", "iit",
    "quantum", "qft", "field theory", "gauge",
    "thermodynamic", "statistical mechanics",
    "schwarzschild", "event horizon", "singularity",
    "wheeler", "it from bit", "participatory universe",
    "hessian", "eigenvalue", "loss landscape",
    "perturbation", "adversarial", "robustness",
    "emergence", "phase transition", "critical",
    "non-commutative", "algebra", "operator",
    "coherence", "decoherence", "measurement"
}

MATH_KEYWORDS = {
    "eigenvalue", "manifold", "topology", "metric",
    "tensor", "differential", "gradient", "hessian",
    "curvature", "geodesic", "symmetry", "group",
    "invariant", "covariant", "measure", "density"
}

FALSIFICATION_KEYWORDS = {
    "falsif", "disprove", "test", "experiment", "predict",
    "measurement", "observable", "evidence", "refute",
    "violation", "contradiction", "inconsistent"
}


class ConvergenceIndexer:
    """Indexes and analyzes convergence session data"""

    def __init__(self, session_path: Path):
        self.session_path = Path(session_path)
        self.session_id = session_path.name
        self.checkpoints = sorted(session_path.glob("checkpoint_*.json"))

        self.index = {
            "session_id": self.session_id,
            "session_path": str(session_path),
            "indexed_at": datetime.utcnow().isoformat(),
            "total_checkpoints": len(self.checkpoints),
            "iterations": [],
            "probe_stats": defaultdict(lambda: {
                "total_responses": 0,
                "total_chars": 0,
                "avg_chars": 0,
                "physics_citations": defaultdict(int),
                "math_citations": defaultdict(int),
                "falsification_mentions": 0,
                "architectures": defaultdict(lambda: {
                    "responses": 0,
                    "total_chars": 0,
                    "avg_chars": 0
                })
            }),
            "architecture_stats": defaultdict(lambda: {
                "total_responses": 0,
                "total_chars": 0,
                "avg_chars": 0,
                "probes_answered": set()
            }),
            "keyword_index": defaultdict(list),  # keyword -> [(probe, arch, iter, snippet)]
            "convergence_patterns": []
        }

    def scan_text_for_keywords(self, text: str, keywords: Set[str]) -> Dict[str, int]:
        """Scan text for physics/math keywords"""
        text_lower = text.lower()
        found = {}
        for keyword in keywords:
            count = len(re.findall(r'\b' + keyword + r'\w*\b', text_lower))
            if count > 0:
                found[keyword] = count
        return found

    def index_checkpoint(self, checkpoint_path: Path):
        """Index a single checkpoint file"""
        with open(checkpoint_path) as f:
            data = json.load(f)

        iteration = data["iteration"]
        timestamp = data["timestamp"]

        iteration_summary = {
            "iteration": iteration,
            "timestamp": timestamp,
            "checkpoint_file": checkpoint_path.name,
            "probes": {}
        }

        for probe_id, responses in data["probe_results"].items():
            probe_summary = {
                "responses": len(responses),
                "total_chars": 0,
                "architectures": {}
            }

            for response_data in responses:
                arch = response_data["architecture"]
                response_text = response_data["response"]
                char_count = len(response_text)

                # Update probe stats
                self.index["probe_stats"][probe_id]["total_responses"] += 1
                self.index["probe_stats"][probe_id]["total_chars"] += char_count
                self.index["probe_stats"][probe_id]["architectures"][arch]["responses"] += 1
                self.index["probe_stats"][probe_id]["architectures"][arch]["total_chars"] += char_count

                # Update architecture stats
                self.index["architecture_stats"][arch]["total_responses"] += 1
                self.index["architecture_stats"][arch]["total_chars"] += char_count
                self.index["architecture_stats"][arch]["probes_answered"].add(probe_id)

                # Scan for keywords
                physics_found = self.scan_text_for_keywords(response_text, PHYSICS_KEYWORDS)
                math_found = self.scan_text_for_keywords(response_text, MATH_KEYWORDS)
                falsif_found = self.scan_text_for_keywords(response_text, FALSIFICATION_KEYWORDS)

                for keyword, count in physics_found.items():
                    self.index["probe_stats"][probe_id]["physics_citations"][keyword] += count
                    # Store snippet for searchability
                    snippet = self._extract_snippet(response_text, keyword)
                    self.index["keyword_index"][keyword].append({
                        "probe": probe_id,
                        "arch": arch,
                        "iteration": iteration,
                        "snippet": snippet
                    })

                for keyword, count in math_found.items():
                    self.index["probe_stats"][probe_id]["math_citations"][keyword] += count

                if falsif_found:
                    self.index["probe_stats"][probe_id]["falsification_mentions"] += 1

                # Architecture summary for this probe
                probe_summary["architectures"][arch] = {
                    "chars": char_count,
                    "physics_keywords": len(physics_found),
                    "math_keywords": len(math_found)
                }
                probe_summary["total_chars"] += char_count

            iteration_summary["probes"][probe_id] = probe_summary

        self.index["iterations"].append(iteration_summary)

    def _extract_snippet(self, text: str, keyword: str, context_chars: int = 200) -> str:
        """Extract snippet around keyword occurrence"""
        text_lower = text.lower()
        idx = text_lower.find(keyword.lower())
        if idx == -1:
            return ""
        start = max(0, idx - context_chars)
        end = min(len(text), idx + len(keyword) + context_chars)
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        return snippet

    def finalize_stats(self):
        """Calculate averages and finalize statistics"""
        # Probe averages
        for probe_id, stats in self.index["probe_stats"].items():
            if stats["total_responses"] > 0:
                stats["avg_chars"] = stats["total_chars"] / stats["total_responses"]

            # Architecture averages per probe
            for arch, arch_stats in stats["architectures"].items():
                if arch_stats["responses"] > 0:
                    arch_stats["avg_chars"] = arch_stats["total_chars"] / arch_stats["responses"]

        # Architecture overall averages
        for arch, stats in self.index["architecture_stats"].items():
            if stats["total_responses"] > 0:
                stats["avg_chars"] = stats["total_chars"] / stats["total_responses"]
            stats["probes_answered"] = list(stats["probes_answered"])  # Convert set to list for JSON

    def generate_index(self) -> Dict:
        """Generate complete index"""
        print(f"📊 Indexing session: {self.session_id}")
        print(f"   Checkpoints to process: {len(self.checkpoints)}")

        for checkpoint_path in self.checkpoints:
            print(f"   Processing {checkpoint_path.name}...")
            self.index_checkpoint(checkpoint_path)

        self.finalize_stats()

        print(f"✓ Index complete")
        print(f"  Total iterations: {len(self.index['iterations'])}")
        print(f"  Unique probes: {len(self.index['probe_stats'])}")
        print(f"  Architectures: {len(self.index['architecture_stats'])}")

        return self.index

    def save_index(self, output_path: Path = None):
        """Save index to JSON"""
        if output_path is None:
            output_path = self.session_path / "SESSION_INDEX.json"

        with open(output_path, 'w') as f:
            json.dump(self.index, f, indent=2)

        print(f"💾 Index saved to: {output_path}")
        return output_path


def index_all_sessions(vault_path: Path = Path("./iris_vault/sessions")):
    """Index all sessions in the vault"""
    sessions = [d for d in vault_path.iterdir() if d.is_dir() and d.name.startswith("MASS_COHERENCE")]

    print(f"\n🔍 IRIS CONVERGENCE DATA INDEXER")
    print(f"   Vault: {vault_path}")
    print(f"   Sessions found: {len(sessions)}\n")

    for session_dir in sorted(sessions):
        indexer = ConvergenceIndexer(session_dir)
        indexer.generate_index()
        indexer.save_index()
        print()


if __name__ == "__main__":
    index_all_sessions()
