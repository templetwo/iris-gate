#!/usr/bin/env python3
"""
Regeneration Outcome Model

Maps bioelectric features → P(regeneration) using logistic regression
coefficients derived from S4 attractor triple co-requirement hypothesis.

Model: P(regen) = sigmoid(β₀ + β₁·center + β₂·rhythm + β₃·aperture + interactions)
"""

import numpy as np
from typing import Dict, List
from vm_ca_gj_sim import BioelectricState

class RegenerationOutcomeModel:
    """Predicts regeneration probability from bioelectric state."""

    def __init__(self, mechanism_map: Dict):
        """
        Initialize with coefficients from mechanism map.
        """
        self.coef = mechanism_map["regeneration_model"]["coefficients"]

    def predict_probability(
        self,
        state_6h: BioelectricState,
        state_24h: BioelectricState
    ) -> Dict[str, float]:
        """
        Predict regeneration outcomes from 6h and 24h states.

        Returns:
            - blastema_24h: P(blastema formation at 24h)
            - regeneration_7d: P(full regeneration at 7d)
            - pattern_fidelity: P(correct patterning)
        """

        # Extract features at 6h (S4 attractor window)
        center_6h = state_6h.center_stability
        rhythm_6h = state_6h.rhythm_coherence
        aperture_6h = state_6h.aperture_permeability

        # Extract features at 24h (blastema formation)
        center_24h = state_24h.center_stability
        rhythm_24h = state_24h.rhythm_coherence

        # Compute logit for blastema formation (24h)
        # Depends primarily on 6h S4 attractor
        logit_blastema = (
            self.coef["intercept"]
            + self.coef["center_stability"] * center_6h
            + self.coef["rhythm_coherence"] * rhythm_6h
            + self.coef["aperture_permeability"] * aperture_6h
            + self.coef["center_rhythm_interaction"] * (center_6h * rhythm_6h)
            + self.coef["rhythm_aperture_interaction"] * (rhythm_6h * aperture_6h)
        )

        p_blastema = self._sigmoid(logit_blastema)

        # Compute logit for full regeneration (7d)
        # Requires blastema formation + sustained center/rhythm at 24h
        logit_regen = (
            self.coef["intercept"] + 0.5  # Slightly easier than blastema
            + self.coef["center_stability"] * center_24h
            + self.coef["rhythm_coherence"] * rhythm_24h
            + self.coef["aperture_permeability"] * aperture_6h  # Early aperture still matters
            + self.coef["center_rhythm_interaction"] * (center_24h * rhythm_24h)
            + 1.5 * p_blastema  # Strong dependence on blastema
        )

        p_regen = self._sigmoid(logit_regen)

        # Pattern fidelity: requires triple co-requirement at 6h + sustained rhythm
        triple_score_6h = center_6h * rhythm_6h * aperture_6h
        rhythm_persistence = rhythm_24h / max(rhythm_6h, 0.1)

        logit_pattern = (
            self.coef["intercept"] + 1.0
            + 4.0 * triple_score_6h  # Very strong dependence on S4 triple
            + 1.5 * rhythm_persistence
        )

        p_pattern = self._sigmoid(logit_pattern)

        return {
            "blastema_24h": p_blastema,
            "regeneration_7d": p_regen,
            "pattern_fidelity": p_pattern
        }

    def predict_with_uncertainty(
        self,
        states_ensemble: List[tuple],  # List of (state_6h, state_24h) tuples
    ) -> Dict[str, Dict[str, float]]:
        """
        Predict regeneration probabilities with uncertainty across ensemble.

        Returns:
            - mean, std, ci_lower, ci_upper for each outcome
        """

        outcomes = {"blastema_24h": [], "regeneration_7d": [], "pattern_fidelity": []}

        for state_6h, state_24h in states_ensemble:
            probs = self.predict_probability(state_6h, state_24h)
            for key in outcomes:
                outcomes[key].append(probs[key])

        # Compute statistics
        results = {}
        for key, values in outcomes.items():
            arr = np.array(values)
            results[key] = {
                "mean": np.mean(arr),
                "std": np.std(arr),
                "ci_lower": np.percentile(arr, 2.5),
                "ci_upper": np.percentile(arr, 97.5),
                "median": np.median(arr)
            }

        return results

    @staticmethod
    def _sigmoid(x: float) -> float:
        """Sigmoid function with overflow protection."""
        if x > 20:
            return 1.0
        elif x < -20:
            return 0.0
        return 1.0 / (1.0 + np.exp(-x))

    def compute_effect_size(
        self,
        outcomes_control: Dict[str, Dict[str, float]],
        outcomes_perturbed: Dict[str, Dict[str, float]],
        outcome_key: str = "regeneration_7d"
    ) -> float:
        """
        Compute Cohen's d effect size between control and perturbed conditions.

        Args:
            outcomes_control: Statistics from control ensemble
            outcomes_perturbed: Statistics from perturbed ensemble
            outcome_key: Which outcome to compare

        Returns:
            Cohen's d (positive = perturbation decreases regeneration)
        """

        mean_ctrl = outcomes_control[outcome_key]["mean"]
        mean_pert = outcomes_perturbed[outcome_key]["mean"]
        std_ctrl = outcomes_control[outcome_key]["std"]
        std_pert = outcomes_perturbed[outcome_key]["std"]

        # Pooled standard deviation
        pooled_std = np.sqrt((std_ctrl**2 + std_pert**2) / 2)

        # Cohen's d (control - perturbed, so positive = perturbation reduces regeneration)
        d = (mean_ctrl - mean_pert) / pooled_std if pooled_std > 0 else 0.0

        return d

class TemporalDynamicsModel:
    """Models temporal evolution of bioelectric states."""

    @staticmethod
    def interpolate_state(
        state_6h: BioelectricState,
        state_24h: BioelectricState,
        target_time_hr: float
    ) -> BioelectricState:
        """Linear interpolation between 6h and 24h states."""

        if target_time_hr <= 6:
            return state_6h
        elif target_time_hr >= 24:
            return state_24h

        # Linear interpolation
        alpha = (target_time_hr - 6) / (24 - 6)

        from vm_ca_gj_sim import BioelectricState

        return BioelectricState(
            time_hr=target_time_hr,
            center_stability=(1-alpha)*state_6h.center_stability + alpha*state_24h.center_stability,
            center_size_mm=(1-alpha)*state_6h.center_size_mm + alpha*state_24h.center_size_mm,
            center_depol_mv=(1-alpha)*state_6h.center_depol_mv + alpha*state_24h.center_depol_mv,
            rhythm_freq_hz=(1-alpha)*state_6h.rhythm_freq_hz + alpha*state_24h.rhythm_freq_hz,
            rhythm_coherence=(1-alpha)*state_6h.rhythm_coherence + alpha*state_24h.rhythm_coherence,
            rhythm_velocity_um_s=(1-alpha)*state_6h.rhythm_velocity_um_s + alpha*state_24h.rhythm_velocity_um_s,
            aperture_permeability=(1-alpha)*state_6h.aperture_permeability + alpha*state_24h.aperture_permeability,
            aperture_dilation_rate=(1-alpha)*state_6h.aperture_dilation_rate + alpha*state_24h.aperture_dilation_rate
        )
