#!/usr/bin/env python3
"""
Monte Carlo Simulation Engine

Runs N replicate simulations per condition to generate distributions
of bioelectric readouts and regeneration outcomes with uncertainty.
"""

import json
import numpy as np
import yaml
from pathlib import Path
from typing import Dict, List
from dataclasses import asdict
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from vm_ca_gj_sim import VMCaGJSimulator, BioelectricState, PerturbationEffect
from outcome_model import RegenerationOutcomeModel

class MonteCarloEngine:
    """Runs Monte Carlo simulations for sandbox experiments."""

    def __init__(self, config: Dict):
        """
        Initialize with:
        - S4 states (all mirrors)
        - Perturbation kits
        - Noise models
        - Mechanism map
        """
        self.config = config
        self.load_resources()

    def load_resources(self):
        """Load all YAML/JSON resources."""

        # Load S4 states
        states_dir = Path("sandbox/states")
        self.s4_states = {}
        for state_file in states_dir.glob("s4_state.*.json"):
            with open(state_file) as f:
                state = json.load(f)
                mirror = state["mirror"]
                self.s4_states[mirror] = state

        # Load perturbation kits
        with open("sandbox/specs/perturbation_kits.yaml") as f:
            self.pert_kits = yaml.safe_load(f)

        # Load readouts
        with open("sandbox/specs/readouts.yaml") as f:
            self.readouts = yaml.safe_load(f)

        # Load mechanism map
        with open("sandbox/engines/mechanisms/s4_to_bioelectric.yaml") as f:
            self.mechanism_map = yaml.safe_load(f)

        # Load noise models
        with open("sandbox/engines/priors/noise_models.yaml") as f:
            self.noise_model = yaml.safe_load(f)

    def run_condition(
        self,
        mirror_name: str,
        perturbations: List[Dict],  # List of {kit, agent, dose}
        n_runs: int,
        timepoints_hr: List[float],
        seed: int = None
    ) -> Dict:
        """
        Run Monte Carlo simulation for one condition on one mirror.

        Returns:
            - timeseries: List of states per run per timepoint
            - outcomes: Regeneration predictions with uncertainty
        """

        rng = np.random.default_rng(seed)

        # Get S4 state for this mirror
        s4_state = self.s4_states[mirror_name]

        # Initialize simulator
        simulator = VMCaGJSimulator(s4_state, self.noise_model, self.mechanism_map)

        # Parse perturbations into PerturbationEffect objects
        pert_effects = self._parse_perturbations(perturbations)

        # Run N simulations
        all_timeseries = []
        states_6h = []
        states_24h = []

        for run_idx in range(n_runs):
            # Simulate timecourse
            states = simulator.simulate_timecourse(pert_effects, timepoints_hr, rng)
            all_timeseries.append(states)

            # Extract 6h and 24h states for outcome prediction
            state_6h = [s for s in states if abs(s.time_hr - 6) < 0.1][0]
            state_24h = [s for s in states if abs(s.time_hr - 24) < 0.1][0]

            states_6h.append(state_6h)
            states_24h.append(state_24h)

        # Predict outcomes
        outcome_model = RegenerationOutcomeModel(self.mechanism_map)
        state_pairs = list(zip(states_6h, states_24h))
        outcomes = outcome_model.predict_with_uncertainty(state_pairs)

        # Aggregate timeseries statistics
        timeseries_stats = self._aggregate_timeseries(all_timeseries, timepoints_hr)

        return {
            "mirror": mirror_name,
            "perturbations": perturbations,
            "n_runs": n_runs,
            "timeseries_stats": timeseries_stats,
            "outcomes": outcomes,
            "raw_states_6h": [asdict(s) for s in states_6h[:10]],  # First 10 as examples
            "raw_states_24h": [asdict(s) for s in states_24h[:10]]
        }

    def run_full_experiment(self, plan: Dict, output_dir: Path) -> Dict:
        """
        Run complete experiment across all mirrors and conditions.

        Args:
            plan: Experiment plan YAML (mirrors, conditions, readouts, n_runs)
            output_dir: Where to save results

        Returns:
            Complete results dictionary
        """

        output_dir.mkdir(parents=True, exist_ok=True)

        mirrors = plan["mirrors"]
        conditions = plan["conditions"]
        n_runs = plan.get("runs", 500)
        timepoints_hr = plan.get("timepoints_hr", [0, 2, 6, 24, 168])

        results = {
            "plan": plan,
            "mirrors": {},
            "consensus": {}
        }

        # Run each condition on each mirror
        for mirror in mirrors:
            print(f"\n=== Running mirror: {mirror} ===")
            results["mirrors"][mirror] = {}

            for condition in conditions:
                label = condition["label"]
                perturbations = condition.get("perturbations", [])

                print(f"  Condition: {label} ({len(perturbations)} perturbations)")

                result = self.run_condition(
                    mirror,
                    perturbations,
                    n_runs,
                    timepoints_hr,
                    seed=hash(f"{mirror}_{label}") % 2**32
                )

                results["mirrors"][mirror][label] = result

                # Print quick summary
                p_regen = result["outcomes"]["regeneration_7d"]["mean"]
                ci = (
                    result["outcomes"]["regeneration_7d"]["ci_lower"],
                    result["outcomes"]["regeneration_7d"]["ci_upper"]
                )
                print(f"    P(regen) = {p_regen:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]")

        # Compute consensus
        print("\n=== Computing cross-mirror consensus ===")
        results["consensus"] = self._compute_consensus(results["mirrors"], conditions)

        # Save results
        output_file = output_dir / "predictions.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to {output_file}")

        return results

    def _parse_perturbations(self, perturbations: List[Dict]) -> List[PerturbationEffect]:
        """Convert perturbation dicts to PerturbationEffect objects."""

        effects = []

        for pert in perturbations:
            kit = pert["kit"]  # "center", "rhythm", "aperture"
            agent = pert["agent"]
            effect_scaling = pert.get("effect_scaling", 1.0)  # Dose scaling factor

            # Look up effect deltas from perturbation_kits.yaml
            agent_spec = self.pert_kits[kit]["agents"][agent]

            deltas = {}
            for key, value in agent_spec.items():
                if key.startswith("effect_on_"):
                    param = key.replace("effect_on_", "")
                    if isinstance(value, dict) and "mean" in value and "std" in value:
                        # Scale effect by dose factor (saturating at 3×)
                        scaled_mean = value["mean"] * min(effect_scaling, 3.0)
                        scaled_std = value["std"] * min(effect_scaling, 3.0)
                        deltas[param] = (scaled_mean, scaled_std)

            effects.append(PerturbationEffect(
                agent=agent,
                target=kit,
                deltas=deltas
            ))

        return effects

    def _aggregate_timeseries(
        self, all_timeseries: List[List[BioelectricState]], timepoints_hr: List[float]
    ) -> Dict:
        """Aggregate timeseries across runs into mean ± CI."""

        stats = {t: {} for t in timepoints_hr}

        for t_idx, t in enumerate(timepoints_hr):
            # Extract all states at this timepoint
            states_at_t = [run[t_idx] for run in all_timeseries]

            # Aggregate each parameter
            for param in ["center_stability", "center_size_mm", "center_depol_mv",
                          "rhythm_freq_hz", "rhythm_coherence", "rhythm_velocity_um_s",
                          "aperture_permeability", "aperture_dilation_rate"]:

                values = np.array([getattr(s, param) for s in states_at_t])

                stats[t][param] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "ci_lower": float(np.percentile(values, 2.5)),
                    "ci_upper": float(np.percentile(values, 97.5)),
                    "median": float(np.median(values))
                }

        return stats

    def _compute_consensus(self, mirror_results: Dict, conditions: List[Dict]) -> Dict:
        """Compute cross-mirror consensus with weighted voting."""

        consensus = {}

        for condition in conditions:
            label = condition["label"]
            consensus[label] = {}

            # Extract P(regeneration) from each mirror
            probs = []
            weights = []

            for mirror, results in mirror_results.items():
                if label in results:
                    p_regen = results[label]["outcomes"]["regeneration_7d"]["mean"]
                    confidence = self.s4_states[mirror]["confidence"]

                    probs.append(p_regen)
                    weights.append(confidence)

            probs = np.array(probs)
            weights = np.array(weights)
            weights /= weights.sum()  # Normalize

            # Weighted consensus
            consensus[label]["regeneration_7d"] = {
                "weighted_mean": float(np.sum(probs * weights)),
                "unweighted_mean": float(np.mean(probs)),
                "std": float(np.std(probs)),
                "min": float(np.min(probs)),
                "max": float(np.max(probs)),
                "agreement": float(1.0 - np.std(probs))  # High agreement = low std
            }

        return consensus

if __name__ == "__main__":
    # Test run
    config = {}
    engine = MonteCarloEngine(config)
    print("✓ Monte Carlo Engine initialized")
    print(f"  Loaded {len(engine.s4_states)} S4 states")
    print(f"  Perturbation kits: {list(engine.pert_kits.keys())}")
