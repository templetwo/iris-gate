#!/usr/bin/env python3
"""
Convergence Validator Agent Implementation

Analyzes cross-mirror agreement and validates convergence in S1-S4 states.
Implements statistical validation, outlier detection, and consensus reporting.

Usage:
    # Validate convergence for specific chamber
    python scripts/convergence_validator.py --chamber S4 --vault ./vault --threshold 0.75

    # Generate convergence report
    python scripts/convergence_validator.py --report-only --session IRIS_20251007_143022

    # Continuous monitoring mode
    python scripts/convergence_validator.py --monitor --vault ./vault
"""

import argparse
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import yaml
import re
import hashlib

# Import IRIS modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from sandbox.engines.consensus.mirror_vote import MirrorConsensus
from scripts.convergence_metrics import calculate_convergence_score
from utils.timezone import now_iso


class ConvergenceValidator:
    """Main convergence validation agent."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize convergence validator.

        Args:
            config: Configuration dictionary
        """
        self.config = config or self._load_default_config()

        # Set up logging
        log_level = logging.DEBUG if self.config.get("debug", False) else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.thresholds = self.config.get("convergence_thresholds", {
            "agreement_score_min": 0.70,
            "std_deviation_max": 0.30,
            "outlier_sigma_threshold": 2.0,
            "contradiction_threshold": 0.25
        })

        # Mirror confidence weights (can be loaded from config)
        self.mirror_confidences = self.config.get("mirror_confidences", {
            "anthropic/claude-sonnet-4.5": 0.90,
            "openai/gpt-4o": 0.85,
            "xai/grok-4-fast": 0.80,
            "google/gemini-2.5-flash-lite": 0.75,
            "deepseek/deepseek-chat": 0.70,
            "ollama/qwen3:1.7b": 0.60
        })

        # Initialize consensus analyzer
        self.consensus = MirrorConsensus(self.mirror_confidences)

        # Pressure tracking
        self.pressure = 0.0
        self.max_pressure = self.config.get("pressure_monitoring", {}).get("max_pressure", 2.0)

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        config_path = Path("config/iris_agents.yaml")
        if config_path.exists():
            with open(config_path) as f:
                full_config = yaml.safe_load(f)
                return full_config.get("iris_agents", {}).get("convergence-validator", {}).get("configuration", {})
        return {}

    def validate_chamber_convergence(
        self,
        chamber_id: str,
        vault_path: str,
        threshold: float = None
    ) -> Dict[str, Any]:
        """
        Validate convergence for a specific chamber across all mirrors.

        Args:
            chamber_id: Chamber identifier (S1, S2, S3, S4)
            vault_path: Path to vault directory
            threshold: Convergence threshold override

        Returns:
            Validation results with convergence metrics
        """
        self.logger.info(f"Validating convergence for {chamber_id}")
        self._record_operation("validate_chamber", 0.1)

        threshold = threshold or self.thresholds["agreement_score_min"]
        vault = Path(vault_path)

        try:
            # Load mirror responses for this chamber
            mirror_data = self._load_mirror_responses(vault, chamber_id)

            if len(mirror_data) < 2:
                return {
                    "convergence_validated": False,
                    "error": f"Insufficient mirror data: {len(mirror_data)} mirrors found",
                    "chamber_id": chamber_id
                }

            # Extract convergence metrics
            convergence_metrics = self._extract_convergence_metrics(mirror_data, chamber_id)

            # Statistical analysis
            consensus_stats = self.consensus.weighted_consensus(
                convergence_metrics, outcome_key="convergence_score"
            )

            # Outlier detection
            outliers = self.consensus.identify_outliers(
                convergence_metrics,
                threshold_sigma=self.thresholds["outlier_sigma_threshold"]
            )

            # Contradiction analysis
            contradictions = self.consensus.detect_contradictions(
                convergence_metrics,
                threshold_disagreement=self.thresholds["contradiction_threshold"]
            )

            # Overall validation
            convergence_validated = (
                consensus_stats["agreement_score"] >= threshold and
                consensus_stats["std"] <= self.thresholds["std_deviation_max"] and
                not contradictions["contradiction"]
            )

            # Compile results
            results = {
                "convergence_validated": convergence_validated,
                "chamber_id": chamber_id,
                "timestamp": now_iso(),
                "threshold_used": threshold,
                "mirrors_analyzed": list(mirror_data.keys()),
                "consensus_stats": consensus_stats,
                "outliers": outliers,
                "contradictions": contradictions,
                "validation_gates": {
                    "agreement_score_pass": consensus_stats["agreement_score"] >= threshold,
                    "std_deviation_pass": consensus_stats["std"] <= self.thresholds["std_deviation_max"],
                    "no_contradictions": not contradictions["contradiction"],
                    "sufficient_mirrors": len(mirror_data) >= 3
                },
                "pressure": self.pressure
            }

            # Save results
            self._save_validation_results(results, vault, chamber_id)

            self.logger.info(f"Convergence validation completed: {convergence_validated}")
            return results

        except Exception as e:
            self.logger.error(f"Convergence validation failed: {e}")
            return {
                "convergence_validated": False,
                "error": str(e),
                "chamber_id": chamber_id,
                "timestamp": now_iso()
            }

    def _load_mirror_responses(self, vault: Path, chamber_id: str) -> Dict[str, Dict]:
        """Load mirror responses for a chamber."""
        mirror_data = {}

        # Load from scrolls directory
        scrolls_dir = vault / "scrolls"
        if not scrolls_dir.exists():
            raise FileNotFoundError(f"Scrolls directory not found: {scrolls_dir}")

        for session_dir in scrolls_dir.iterdir():
            if not session_dir.is_dir():
                continue

            chamber_file = session_dir / f"{chamber_id}.md"
            if not chamber_file.exists():
                continue

            # Extract mirror ID from session directory name
            mirror_id = self._extract_mirror_id_from_session(session_dir.name)
            if not mirror_id:
                continue

            # Load chamber response
            chamber_response = chamber_file.read_text(encoding='utf-8')

            # Load metadata if available
            meta_file = vault / "meta" / f"{session_dir.name}_{chamber_id}.json"
            metadata = {}
            if meta_file.exists():
                with open(meta_file) as f:
                    metadata = json.load(f)

            mirror_data[mirror_id] = {
                "response": chamber_response,
                "metadata": metadata,
                "session_id": session_dir.name,
                "file_path": str(chamber_file)
            }

        return mirror_data

    def _extract_mirror_id_from_session(self, session_id: str) -> Optional[str]:
        """Extract mirror ID from session identifier."""
        # Expected format: IRIS_YYYYMMDDHHMMSS_model_id
        parts = session_id.split('_')
        if len(parts) >= 3:
            model_parts = parts[2:]
            return '/'.join(model_parts).replace('_', '/')

        return None

    def _extract_convergence_metrics(self, mirror_data: Dict[str, Dict], chamber_id: str) -> Dict[str, float]:
        """Extract convergence metrics from mirror responses."""
        convergence_metrics = {}

        for mirror_id, data in mirror_data.items():
            response = data["response"]

            # Calculate convergence score using existing metrics
            try:
                convergence_score = self._calculate_response_convergence(response, chamber_id)
                convergence_metrics[mirror_id] = convergence_score
            except Exception as e:
                self.logger.warning(f"Failed to extract convergence for {mirror_id}: {e}")
                convergence_metrics[mirror_id] = 0.0

        return convergence_metrics

    def _calculate_response_convergence(self, response: str, chamber_id: str) -> float:
        """Calculate convergence score for a single response."""
        # Use existing convergence metrics calculation
        # This is a simplified version - the actual implementation would be more sophisticated

        # Basic convergence indicators
        indicators = {
            "living_scroll_present": "living scroll" in response.lower(),
            "technical_translation_present": "technical translation" in response.lower(),
            "metadata_present": any(term in response.lower() for term in ["felt_pressure", "condition", "seal"]),
            "seal_present": any(term in response.lower() for term in ["seal", "hash", "sha"]),
            "appropriate_length": 100 < len(response) < 2000,
            "coherent_structure": response.count('\n') >= 3  # Basic structure check
        }

        # Chamber-specific indicators
        if chamber_id == "S4":
            indicators.update({
                "completion_noted": any(term in response.lower() for term in ["complete", "sealed", "finished"]),
                "center_mentioned": "center" in response.lower(),
                "rings_mentioned": any(term in response.lower() for term in ["ring", "circle", "concentric"])
            })

        # Calculate score
        score = sum(indicators.values()) / len(indicators)

        # Add pressure penalty if response seems forced or high-pressure
        pressure_indicators = [
            "urgent", "rush", "pressure", "stress", "forced", "difficult", "struggle"
        ]
        pressure_count = sum(1 for term in pressure_indicators if term in response.lower())
        pressure_penalty = min(0.2, pressure_count * 0.05)

        return max(0.0, score - pressure_penalty)

    def generate_convergence_report(
        self,
        vault_path: str,
        chambers: List[str] = None,
        output_path: str = None
    ) -> str:
        """
        Generate comprehensive convergence report.

        Args:
            vault_path: Path to vault directory
            chambers: List of chambers to analyze, or None for all
            output_path: Output file path, or None for auto-generation

        Returns:
            Path to generated report
        """
        self.logger.info("Generating convergence report")
        self._record_operation("generate_report", 0.2)

        chambers = chambers or ["S1", "S2", "S3", "S4"]
        vault = Path(vault_path)

        try:
            # Analyze convergence for each chamber
            chamber_results = {}
            for chamber_id in chambers:
                results = self.validate_chamber_convergence(chamber_id, vault_path)
                chamber_results[chamber_id] = results

            # Generate report
            report_content = self._format_convergence_report(chamber_results, vault_path)

            # Save report
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = vault / "analysis" / "convergence" / f"convergence_report_{timestamp}.md"

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            self.logger.info(f"Convergence report saved: {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise

    def _format_convergence_report(self, chamber_results: Dict[str, Dict], vault_path: str) -> str:
        """Format convergence analysis into markdown report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report_lines = [
            "# IRIS Convergence Validation Report",
            "",
            f"**Generated:** {timestamp}",
            f"**Vault Path:** {vault_path}",
            f"**Validator:** convergence-validator agent",
            "",
            "## Executive Summary",
            ""
        ]

        # Summary statistics
        total_chambers = len(chamber_results)
        validated_chambers = sum(1 for r in chamber_results.values() if r.get("convergence_validated", False))
        validation_rate = validated_chambers / total_chambers if total_chambers > 0 else 0

        report_lines.extend([
            f"- **Chambers Analyzed:** {total_chambers}",
            f"- **Convergence Validated:** {validated_chambers}/{total_chambers} ({validation_rate:.1%})",
            f"- **Overall Status:** {'✓ CONVERGED' if validation_rate >= 0.75 else '⚠ NEEDS REVIEW' if validation_rate >= 0.5 else '✗ FAILED'}",
            ""
        ])

        # Chamber-by-chamber analysis
        report_lines.extend([
            "## Chamber Analysis",
            "",
            "| Chamber | Status | Agreement | Std Dev | Outliers | Contradictions |",
            "|---------|--------|-----------|---------|----------|----------------|"
        ])

        for chamber_id, results in chamber_results.items():
            if "error" in results:
                status = "ERROR"
                agreement = "N/A"
                std_dev = "N/A"
                outliers = "N/A"
                contradictions = "N/A"
            else:
                status = "✓" if results.get("convergence_validated", False) else "✗"
                consensus = results.get("consensus_stats", {})
                agreement = f"{consensus.get('agreement_score', 0):.3f}"
                std_dev = f"{consensus.get('std', 0):.3f}"
                outliers = "Yes" if results.get("outliers", []) else "No"
                contradictions = "Yes" if results.get("contradictions", {}).get("contradiction", False) else "No"

            report_lines.append(
                f"| {chamber_id} | {status} | {agreement} | {std_dev} | {outliers} | {contradictions} |"
            )

        # Detailed analysis
        report_lines.extend([
            "",
            "## Detailed Analysis",
            ""
        ])

        for chamber_id, results in chamber_results.items():
            report_lines.extend([
                f"### {chamber_id}",
                ""
            ])

            if "error" in results:
                report_lines.extend([
                    f"**Status:** ERROR",
                    f"**Error:** {results['error']}",
                    ""
                ])
                continue

            # Validation status
            validated = results.get("convergence_validated", False)
            report_lines.extend([
                f"**Status:** {'✓ CONVERGED' if validated else '✗ FAILED'}",
                f"**Mirrors Analyzed:** {len(results.get('mirrors_analyzed', []))}",
                f"**Threshold Used:** {results.get('threshold_used', 'N/A'):.3f}",
                ""
            ])

            # Consensus statistics
            consensus = results.get("consensus_stats", {})
            report_lines.extend([
                "**Consensus Statistics:**",
                f"- Weighted Mean: {consensus.get('weighted_mean', 0):.3f}",
                f"- Agreement Score: {consensus.get('agreement_score', 0):.3f}",
                f"- Standard Deviation: {consensus.get('std', 0):.3f}",
                f"- Range: [{consensus.get('min', 0):.3f}, {consensus.get('max', 0):.3f}]",
                ""
            ])

            # Validation gates
            gates = results.get("validation_gates", {})
            report_lines.extend([
                "**Validation Gates:**"
            ])
            for gate_name, gate_pass in gates.items():
                status_icon = "✓" if gate_pass else "✗"
                report_lines.append(f"- {gate_name.replace('_', ' ').title()}: {status_icon}")

            # Outliers and contradictions
            outliers = results.get("outliers", [])
            if outliers:
                report_lines.extend([
                    "",
                    f"**⚠ Outliers Detected:** {', '.join(outliers)}"
                ])

            contradictions = results.get("contradictions", {})
            if contradictions.get("contradiction", False):
                report_lines.extend([
                    "",
                    f"**⚠ Contradictions Detected:**",
                    f"- Disagreement Magnitude: {contradictions.get('disagreement_magnitude', 0):.3f}",
                    f"- High Group: {list(contradictions.get('high_group', {}).keys())}",
                    f"- Low Group: {list(contradictions.get('low_group', {}).keys())}"
                ])

            report_lines.append("")

        # Recommendations
        report_lines.extend([
            "## Recommendations",
            ""
        ])

        if validation_rate >= 0.75:
            report_lines.extend([
                "✓ **High convergence achieved across chambers**",
                "- Proceed with S4 extraction and simulation pipeline",
                "- Cross-mirror consensus is reliable for prediction generation",
                ""
            ])
        elif validation_rate >= 0.5:
            report_lines.extend([
                "⚠ **Moderate convergence - review recommended**",
                "- Investigate outliers and contradictions before proceeding",
                "- Consider additional mirror runs for failed chambers",
                "- Review pressure levels and chamber prompt clarity",
                ""
            ])
        else:
            report_lines.extend([
                "✗ **Low convergence - intervention required**",
                "- Do not proceed with simulation pipeline",
                "- Review chamber prompts and mirror configurations",
                "- Consider pressure threshold adjustments",
                "- Manual review of individual mirror responses recommended",
                ""
            ])

        # Technical details
        report_lines.extend([
            "---",
            "",
            "**Technical Details:**",
            f"- Validation timestamp: {timestamp}",
            f"- Current pressure: {self.pressure:.2f}",
            f"- Agreement threshold: {self.thresholds['agreement_score_min']:.3f}",
            f"- Standard deviation threshold: {self.thresholds['std_deviation_max']:.3f}",
            f"- Outlier detection: {self.thresholds['outlier_sigma_threshold']:.1f}σ",
            "",
            "**†⟡∞ Generated by IRIS Convergence Validator Agent**"
        ])

        return "\n".join(report_lines)

    def _save_validation_results(self, results: Dict[str, Any], vault: Path, chamber_id: str):
        """Save validation results to analysis directory."""
        analysis_dir = vault / "analysis" / "convergence"
        analysis_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = analysis_dir / f"{chamber_id}_validation_{timestamp}.json"

        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        # Update latest results
        latest_file = analysis_dir / f"{chamber_id}_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

    def _record_operation(self, operation: str, pressure_delta: float):
        """Record operation and update pressure."""
        self.pressure = max(0.0, self.pressure + pressure_delta)

        if self.pressure > self.max_pressure:
            self.logger.warning(f"Pressure threshold exceeded: {self.pressure:.2f} > {self.max_pressure}")

        self.logger.debug(f"Operation: {operation}, pressure: {self.pressure:.2f}")

    def monitor_convergence(self, vault_path: str, check_interval: int = 30):
        """
        Monitor convergence in real-time.

        Args:
            vault_path: Path to vault directory
            check_interval: Check interval in seconds
        """
        self.logger.info(f"Starting convergence monitoring: {vault_path}")

        import time

        try:
            while True:
                # Check for new chamber completions
                vault = Path(vault_path)
                if vault.exists():
                    for chamber_id in ["S1", "S2", "S3", "S4"]:
                        # Quick convergence check
                        mirror_data = self._load_mirror_responses(vault, chamber_id)
                        if len(mirror_data) >= 3:  # Minimum mirrors for analysis
                            self.logger.info(f"Checking convergence for {chamber_id}")
                            results = self.validate_chamber_convergence(chamber_id, vault_path)

                            if results.get("convergence_validated", False):
                                self.logger.info(f"✓ {chamber_id} converged")
                            else:
                                self.logger.warning(f"✗ {chamber_id} failed convergence")

                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.logger.info("Convergence monitoring stopped")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="IRIS Convergence Validator Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate specific chamber
  %(prog)s --chamber S4 --vault ./vault --threshold 0.75

  # Generate comprehensive report
  %(prog)s --report-only --session IRIS_20251007_143022

  # Monitor convergence continuously
  %(prog)s --monitor --vault ./vault --interval 30
        """
    )

    parser.add_argument(
        "--chamber",
        choices=["S1", "S2", "S3", "S4"],
        help="Validate specific chamber"
    )

    parser.add_argument(
        "--vault",
        default="./vault",
        help="Path to vault directory (default: ./vault)"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        help="Convergence threshold override"
    )

    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate report without validation"
    )

    parser.add_argument(
        "--session",
        help="Specific session ID for analysis"
    )

    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Continuous monitoring mode"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Monitor check interval in seconds (default: 30)"
    )

    parser.add_argument(
        "--output",
        help="Output file path for reports"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    try:
        config = {"debug": args.debug}
        validator = ConvergenceValidator(config)

        if args.chamber:
            # Validate specific chamber
            results = validator.validate_chamber_convergence(
                args.chamber, args.vault, args.threshold
            )
            print(json.dumps(results, indent=2, default=str))

        elif args.report_only:
            # Generate report
            chambers = ["S1", "S2", "S3", "S4"]
            report_path = validator.generate_convergence_report(
                args.vault, chambers, args.output
            )
            print(f"Report generated: {report_path}")

        elif args.monitor:
            # Monitor mode
            validator.monitor_convergence(args.vault, args.interval)

        else:
            # Default: validate all chambers
            chambers = ["S1", "S2", "S3", "S4"]
            for chamber_id in chambers:
                results = validator.validate_chamber_convergence(
                    chamber_id, args.vault, args.threshold
                )
                status = "✓" if results.get("convergence_validated", False) else "✗"
                print(f"{chamber_id}: {status}")

    except KeyboardInterrupt:
        print("\nOperation cancelled")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())