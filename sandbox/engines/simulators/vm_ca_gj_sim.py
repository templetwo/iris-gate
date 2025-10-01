#!/usr/bin/env python3
"""
Voltage / Calcium / Gap Junction Forward Simulator

Generates time-series predictions for bioelectric readouts based on:
1. S4 frozen state priors (from converged attractor)
2. Perturbation deltas (from perturbation_kits.yaml)
3. Noise models (biological + measurement variability)

This is a phenomenological model, not biophysical. It captures the
relationships encoded in S4→bioelectric mapping without solving PDEs.
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class BioelectricState:
    """Snapshot of bioelectric parameters at a timepoint."""
    time_hr: float

    # Voltage (center)
    center_stability: float
    center_size_mm: float
    center_depol_mv: float

    # Calcium (rhythm)
    rhythm_freq_hz: float
    rhythm_coherence: float
    rhythm_velocity_um_s: float

    # Gap junction (aperture)
    aperture_permeability: float
    aperture_dilation_rate: float

@dataclass
class PerturbationEffect:
    """Applied perturbation with effect deltas."""
    agent: str
    target: str  # "center", "rhythm", "aperture"

    # Effect deltas (mean ± std)
    deltas: Dict[str, Tuple[float, float]]  # param_name → (mean, std)

class VMCaGJSimulator:
    """Forward simulator for bioelectric dynamics."""

    def __init__(self, s4_state: Dict, noise_model: Dict, mechanism_map: Dict):
        """
        Initialize simulator with:
        - s4_state: Frozen S4 attractor priors for one mirror
        - noise_model: Noise parameters (biological + measurement)
        - mechanism_map: S4 triple → bioelectric mapping
        """
        self.s4_state = s4_state
        self.noise_model = noise_model
        self.mechanism_map = mechanism_map

    def sample_initial_state(self, rng: np.random.Generator) -> BioelectricState:
        """Sample initial state from S4 priors + noise."""

        # Extract priors
        rhythm_priors = self.s4_state["triple_signature"]["rhythm"]
        center_priors = self.s4_state["triple_signature"]["center"]
        aperture_priors = self.s4_state["triple_signature"]["aperture"]

        # Sample with noise (scaled by mirror confidence)
        confidence = self.s4_state["confidence"]
        noise_scale = 1.0 / np.sqrt(confidence)

        # Voltage (center)
        center_stability = self._sample_from_range(
            center_priors["stability_prior"], rng, noise_scale * 0.15
        )
        center_size = self._sample_from_range(
            center_priors["size_mm_prior"], rng, noise_scale * 0.20
        )
        center_depol = self._sample_from_range(
            center_priors["depol_mv_prior"], rng, noise_scale * 0.15
        )

        # Calcium (rhythm)
        rhythm_freq = self._sample_from_range(
            rhythm_priors["freq_hz_prior"], rng, noise_scale * 0.20
        )
        rhythm_coherence = self._sample_from_range(
            rhythm_priors["coherence_prior"], rng, noise_scale * 0.15
        )
        rhythm_velocity = self._sample_from_range(
            rhythm_priors["velocity_um_s_prior"], rng, noise_scale * 0.25
        )

        # Gap junction (aperture)
        aperture_perm = self._sample_from_range(
            aperture_priors["permeability_prior"], rng, noise_scale * 0.20
        )
        aperture_dilation = self._sample_from_range(
            aperture_priors["dilation_rate_prior"], rng, noise_scale * 0.25
        )

        return BioelectricState(
            time_hr=0.0,
            center_stability=center_stability,
            center_size_mm=center_size,
            center_depol_mv=center_depol,
            rhythm_freq_hz=rhythm_freq,
            rhythm_coherence=rhythm_coherence,
            rhythm_velocity_um_s=rhythm_velocity,
            aperture_permeability=aperture_perm,
            aperture_dilation_rate=aperture_dilation
        )

    def apply_perturbation(
        self,
        state: BioelectricState,
        perturbations: List[PerturbationEffect],
        rng: np.random.Generator
    ) -> BioelectricState:
        """Apply perturbation effects to current state."""

        new_state = BioelectricState(**state.__dict__)

        for pert in perturbations:
            if pert.target == "center":
                if "center_stability" in pert.deltas:
                    delta_mean, delta_std = pert.deltas["center_stability"]
                    delta = rng.normal(delta_mean, delta_std)
                    new_state.center_stability = np.clip(
                        new_state.center_stability * (1 + delta), 0.0, 1.0
                    )

                if "center_size" in pert.deltas:
                    delta_mean, delta_std = pert.deltas["center_size"]
                    delta = rng.normal(delta_mean, delta_std)
                    new_state.center_size_mm = np.clip(
                        new_state.center_size_mm * (1 + delta), 0.0, 2.0
                    )

                if "depol_mv" in pert.deltas:
                    delta_mean, delta_std = pert.deltas["depol_mv"]
                    delta = rng.normal(delta_mean, delta_std)
                    new_state.center_depol_mv = np.clip(
                        new_state.center_depol_mv + delta, -10, 60
                    )

            elif pert.target == "rhythm":
                if "rhythm_freq" in pert.deltas:
                    delta_mean, delta_std = pert.deltas["rhythm_freq"]
                    delta = rng.normal(delta_mean, delta_std)
                    new_state.rhythm_freq_hz = np.clip(
                        new_state.rhythm_freq_hz * (1 + delta), 0.1, 5.0
                    )

                if "rhythm_coherence" in pert.deltas:
                    delta_mean, delta_std = pert.deltas["rhythm_coherence"]
                    delta = rng.normal(delta_mean, delta_std)
                    new_state.rhythm_coherence = np.clip(
                        new_state.rhythm_coherence * (1 + delta), 0.0, 1.0
                    )

                if "velocity" in pert.deltas:
                    delta_mean, delta_std = pert.deltas["velocity"]
                    delta = rng.normal(delta_mean, delta_std)
                    new_state.rhythm_velocity_um_s = np.clip(
                        new_state.rhythm_velocity_um_s * (1 + delta), 5, 100
                    )

            elif pert.target == "aperture":
                if "permeability" in pert.deltas:
                    delta_mean, delta_std = pert.deltas["permeability"]
                    delta = rng.normal(delta_mean, delta_std)
                    new_state.aperture_permeability = np.clip(
                        new_state.aperture_permeability * (1 + delta), 0.0, 1.0
                    )

                if "dilation_rate" in pert.deltas:
                    delta_mean, delta_std = pert.deltas["dilation_rate"]
                    delta = rng.normal(delta_mean, delta_std)
                    new_state.aperture_dilation_rate = np.clip(
                        new_state.aperture_dilation_rate * (1 + delta), 0.0, 1.0
                    )

        # Apply triple coupling effects (from mechanism map)
        new_state = self._apply_triple_coupling(state, new_state)

        return new_state

    def _apply_triple_coupling(
        self, original: BioelectricState, perturbed: BioelectricState
    ) -> BioelectricState:
        """Apply center-rhythm-aperture coupling effects."""

        # Center-rhythm coupling
        # If center is disrupted, rhythm coherence drops
        center_disruption = max(0, original.center_stability - perturbed.center_stability)
        coupling_coeff = 0.4  # From mechanism map
        perturbed.rhythm_coherence *= (1 - coupling_coeff * center_disruption)

        # Rhythm-aperture resonance
        # If either rhythm or aperture is disrupted, the other suffers
        freq_optimal = 1.0  # Hz
        perm_optimal = 0.8
        freq_deviation = abs(perturbed.rhythm_freq_hz - freq_optimal) / freq_optimal
        perm_deviation = abs(perturbed.aperture_permeability - perm_optimal) / perm_optimal

        resonance_penalty = 0.3 * (freq_deviation + perm_deviation)
        perturbed.rhythm_coherence *= (1 - resonance_penalty)
        perturbed.aperture_permeability *= (1 - resonance_penalty)

        # Aperture gates center formation
        # If aperture is very low, center cannot form
        if perturbed.aperture_permeability < 0.3:
            perturbed.center_stability *= 0.5
            perturbed.center_size_mm *= 0.6

        return perturbed

    def simulate_timecourse(
        self,
        perturbations: List[PerturbationEffect],
        timepoints_hr: List[float],
        rng: np.random.Generator
    ) -> List[BioelectricState]:
        """Simulate timecourse with perturbations."""

        # Sample initial state
        state = self.sample_initial_state(rng)

        # Apply perturbations (assumed to take effect immediately)
        state = self.apply_perturbation(state, perturbations, rng)

        # Generate timecourse (simple: state persists with temporal dynamics)
        states = []
        for t in timepoints_hr:
            # Add temporal dynamics
            state_t = self._evolve_state(state, t, rng)
            states.append(state_t)

        return states

    def _evolve_state(
        self, base_state: BioelectricState, time_hr: float, rng: np.random.Generator
    ) -> BioelectricState:
        """Evolve state with temporal dynamics."""

        state = BioelectricState(**base_state.__dict__)
        state.time_hr = time_hr

        # Aperture dynamics: peaks at 2-4h, then declines
        peak_time = rng.uniform(2, 4)
        if time_hr < peak_time:
            # Approaching peak
            aperture_boost = 1.0 + 0.5 * (time_hr / peak_time)
        else:
            # Declining from peak
            aperture_boost = 1.0 + 0.5 * np.exp(-(time_hr - peak_time) / 6.0)

        state.aperture_permeability *= np.clip(aperture_boost, 0.5, 1.5)

        # Center stability: forms by 6h, persists to 24h, then decays
        if time_hr < 6:
            center_ramp = time_hr / 6.0
        elif time_hr < 24:
            center_ramp = 1.0
        else:
            center_ramp = np.exp(-(time_hr - 24) / 48.0)

        state.center_stability *= np.clip(center_ramp, 0.3, 1.0)

        # Rhythm: stable 6-24h, slight decay after
        if time_hr < 6:
            rhythm_ramp = 0.7 + 0.3 * (time_hr / 6.0)
        elif time_hr < 24:
            rhythm_ramp = 1.0
        else:
            rhythm_ramp = 0.85

        state.rhythm_coherence *= rhythm_ramp

        # Add measurement noise
        state.center_depol_mv += rng.normal(0, 3.0)  # mV
        state.rhythm_freq_hz += rng.normal(0, 0.1)  # Hz

        return state

    def _sample_from_range(
        self, prior_range: List[float], rng: np.random.Generator, noise_cv: float
    ) -> float:
        """Sample from uniform prior range with added noise."""
        low, high = prior_range
        base_value = rng.uniform(low, high)
        noise = rng.normal(0, noise_cv * base_value)
        return np.clip(base_value + noise, low * 0.5, high * 1.5)
