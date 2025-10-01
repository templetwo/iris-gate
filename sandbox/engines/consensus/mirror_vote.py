#!/usr/bin/env python3
"""
Cross-Mirror Consensus Analysis

Aggregates predictions across mirrors with confidence weighting,
identifies agreements and contradictions, flags outliers for human review.
"""

import numpy as np
from typing import Dict, List

class MirrorConsensus:
    """Analyze cross-mirror agreement and contradictions."""

    def __init__(self, mirror_confidences: Dict[str, float]):
        """Initialize with mirror confidence scores."""
        self.confidences = mirror_confidences

    def weighted_consensus(
        self,
        mirror_predictions: Dict[str, float],
        outcome_key: str = "regeneration_7d"
    ) -> Dict:
        """
        Compute weighted consensus across mirrors.

        Args:
            mirror_predictions: {mirror_name: prediction_value}
            outcome_key: Which outcome we're aggregating

        Returns:
            Consensus statistics with agreement metrics
        """

        mirrors = list(mirror_predictions.keys())
        values = np.array([mirror_predictions[m] for m in mirrors])
        weights = np.array([self.confidences.get(m, 0.8) for m in mirrors])
        weights /= weights.sum()

        weighted_mean = np.sum(values * weights)
        unweighted_mean = np.mean(values)
        std = np.std(values)

        # Agreement score (1.0 = perfect agreement, 0.0 = total disagreement)
        agreement = 1.0 - min(std / unweighted_mean, 1.0) if unweighted_mean > 0 else 0.0

        return {
            "weighted_mean": float(weighted_mean),
            "unweighted_mean": float(unweighted_mean),
            "std": float(std),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "range": float(np.max(values) - np.min(values)),
            "agreement_score": float(agreement),
            "n_mirrors": len(mirrors)
        }

    def identify_outliers(
        self,
        mirror_predictions: Dict[str, float],
        threshold_sigma: float = 2.0
    ) -> List[str]:
        """
        Identify mirrors with outlier predictions (> threshold_sigma from mean).

        Returns:
            List of mirror names that are outliers
        """

        values = np.array(list(mirror_predictions.values()))
        mean = np.mean(values)
        std = np.std(values)

        outliers = []
        for mirror, value in mirror_predictions.items():
            if abs(value - mean) > threshold_sigma * std:
                outliers.append(mirror)

        return outliers

    def detect_contradictions(
        self,
        mirror_predictions: Dict[str, float],
        threshold_disagreement: float = 0.3
    ) -> Dict:
        """
        Detect contradictions: mirrors predicting opposite outcomes.

        Args:
            mirror_predictions: {mirror_name: P(outcome)}
            threshold_disagreement: If max-min > this, flag as contradiction

        Returns:
            Contradiction report with high/low groups
        """

        values = list(mirror_predictions.values())
        disagreement = max(values) - min(values)

        if disagreement < threshold_disagreement:
            return {"contradiction": False}

        # Split into high/low groups
        median = np.median(values)
        high_group = {m: v for m, v in mirror_predictions.items() if v > median}
        low_group = {m: v for m, v in mirror_predictions.items() if v <= median}

        return {
            "contradiction": True,
            "disagreement_magnitude": float(disagreement),
            "high_group": high_group,
            "low_group": low_group,
            "interpretation": f"Mirrors split: {len(high_group)} predict high, {len(low_group)} predict low"
        }

    def generate_consensus_report(
        self,
        all_results: Dict,  # Full results from monte_carlo.py
        conditions: List[str]
    ) -> str:
        """
        Generate human-readable consensus report.

        Returns:
            Markdown-formatted report
        """

        report_lines = [
            "# Cross-Mirror Consensus Report",
            "",
            "## Overview",
            f"- Mirrors analyzed: {len(all_results['mirrors'])}",
            f"- Conditions tested: {len(conditions)}",
            "",
            "## Condition-by-Condition Consensus",
            ""
        ]

        for condition_label in conditions:
            report_lines.append(f"### {condition_label}")
            report_lines.append("")

            # Extract predictions from each mirror
            mirror_preds = {}
            for mirror, results in all_results["mirrors"].items():
                if condition_label in results:
                    p_regen = results[condition_label]["outcomes"]["regeneration_7d"]["mean"]
                    mirror_preds[mirror] = p_regen

            # Compute consensus
            consensus = self.weighted_consensus(mirror_preds)

            report_lines.append(f"**Consensus P(regeneration):** {consensus['weighted_mean']:.3f}")
            report_lines.append(f"- Range: [{consensus['min']:.3f}, {consensus['max']:.3f}]")
            report_lines.append(f"- Agreement score: {consensus['agreement_score']:.2f}/1.00")

            # Check for outliers
            outliers = self.identify_outliers(mirror_preds)
            if outliers:
                report_lines.append(f"- ⚠️ **Outliers detected:** {', '.join(outliers)}")

            # Check for contradictions
            contradiction = self.detect_contradictions(mirror_preds)
            if contradiction["contradiction"]:
                report_lines.append(f"- ⚠️ **Contradiction detected** (disagreement={contradiction['disagreement_magnitude']:.2f})")
                report_lines.append(f"  - High group: {list(contradiction['high_group'].keys())}")
                report_lines.append(f"  - Low group: {list(contradiction['low_group'].keys())}")

            report_lines.append("")

        # Summary table
        report_lines.append("## Summary Table")
        report_lines.append("")
        report_lines.append("| Condition | Consensus P(regen) | Range | Agreement | Outliers | Contradiction |")
        report_lines.append("|-----------|-------------------|-------|-----------|----------|---------------|")

        for condition_label in conditions:
            mirror_preds = {}
            for mirror, results in all_results["mirrors"].items():
                if condition_label in results:
                    p_regen = results[condition_label]["outcomes"]["regeneration_7d"]["mean"]
                    mirror_preds[mirror] = p_regen

            consensus = self.weighted_consensus(mirror_preds)
            outliers = self.identify_outliers(mirror_preds)
            contradiction = self.detect_contradictions(mirror_preds)

            outlier_str = "Yes" if outliers else "No"
            contradiction_str = "Yes" if contradiction["contradiction"] else "No"

            report_lines.append(
                f"| {condition_label} | {consensus['weighted_mean']:.3f} | "
                f"[{consensus['min']:.3f}, {consensus['max']:.3f}] | "
                f"{consensus['agreement_score']:.2f} | {outlier_str} | {contradiction_str} |"
            )

        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("**Interpretation:**")
        report_lines.append("- **Agreement score > 0.90:** High confidence in consensus prediction")
        report_lines.append("- **Agreement score 0.70-0.90:** Moderate confidence, minor variance across mirrors")
        report_lines.append("- **Agreement score < 0.70:** Low confidence, significant disagreement → design wet-lab experiment to resolve")
        report_lines.append("")
        report_lines.append("**†⟡∞ Generated by IRIS Sandbox Simulator**")

        return "\n".join(report_lines)
