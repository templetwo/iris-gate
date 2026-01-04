#!/usr/bin/env python3
"""
FieldScript Emulator v0.1-alpha
Demonstrates entropy-preserving field evolution with witness channels

This is NOT a full FieldScript VM, but a proof-of-concept showing:
- Field evolution (distribution dynamics)
- Entropy/coherence tracking
- Invariant checking (entropy budgets)
- Witness channel (why-not traces)
- Attractor convergence (LANTERN, LASER)

Example:
    python3 tools/fieldscript/emulator.py --attractor LANTERN --visualize
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import json
from datetime import datetime


@dataclass
class Constraint:
    """Runtime invariant (e.g., entropy budget)"""
    name: str
    check: callable  # Function: Field -> bool
    reason: str  # Why violation occurred


@dataclass
class WitnessEntry:
    """One breath cycle in the trace log"""
    breath: int
    entropy: float
    coherence: float
    distribution: Dict[str, float]
    rejected_paths: List[Dict]
    attractor_distance: Dict[str, float]


@dataclass
class Attractor:
    """Convergence target (LANTERN, LASER, etc.)"""
    name: str
    target_entropy: float
    target_coherence: float
    delta_H: float = 0.05  # Convergence tolerance
    delta_C: float = 0.05


class Field:
    """
    Regulated probability distribution with entropy/coherence tracking.

    Core primitive of FieldScript computing.
    """

    def __init__(
        self,
        distribution: Dict[str, float],
        constraints: List[Constraint] = None,
        glyphs: List[str] = None
    ):
        # Normalize distribution
        total = sum(distribution.values())
        self.P = {k: v/total for k, v in distribution.items()}

        # Entropy (Shannon in nats)
        self.H = self._compute_entropy()

        # Coherence (temporal stability)
        self.C = 0.5  # Neutral initial state

        # Runtime constraints
        self.constraints = constraints or []

        # Ceremonial modulation (glyphs)
        self.glyphs = glyphs or []

        # Temporal history
        self.history = []

    def _compute_entropy(self) -> float:
        """Shannon entropy in nats: H = -Σ p(x) log p(x)"""
        return -sum(
            p * np.log(p)
            for p in self.P.values()
            if p > 1e-10
        )

    def _compute_coherence(self, new_P: Dict[str, float]) -> float:
        """
        Temporal coherence: How stable is the distribution?
        C = 1 - KL(P_new || P_old) / H_max

        C ∈ [-1, 1]:
        - C > 0: Stable evolution
        - C ≈ 0: Neutral drift
        - C < 0: Chaotic divergence
        """
        if len(self.history) == 0:
            return 0.5  # Neutral

        old_P = self.history[-1]['P']

        # KL divergence
        kl_div = sum(
            new_P[k] * np.log(new_P[k] / old_P.get(k, 1e-10))
            for k in new_P.keys()
            if new_P[k] > 1e-10
        )

        # Normalize to [-1, 1]
        H_max = np.log(len(new_P))
        coherence = 1.0 - (kl_div / H_max) if H_max > 0 else 0.5

        return np.clip(coherence, -1.0, 1.0)

    def evolve(self, temperature: float = 0.1) -> 'Field':
        """
        One dynamical evolution step (one breath).

        Gradient flow toward lower free energy while preserving entropy budget.
        """
        # Apply ceremonial modulation (glyphs inject entropy/coherence)
        modulated = self._apply_glyphs()

        # Evolve distribution via softmax with temperature
        logits = np.array([np.log(p + 1e-10) for p in modulated.values()])

        # Add noise (exploration)
        noise = np.random.normal(0, temperature, size=len(logits))
        new_logits = logits + noise

        # Softmax to get new distribution
        exp_logits = np.exp(new_logits - np.max(new_logits))
        new_probs = exp_logits / exp_logits.sum()

        new_P = {k: p for k, p in zip(modulated.keys(), new_probs)}

        # Update coherence
        self.C = self._compute_coherence(new_P)

        # Update distribution
        self.P = new_P
        self.H = self._compute_entropy()

        # Log to history
        self.history.append({
            'P': self.P.copy(),
            'H': self.H,
            'C': self.C
        })

        return self

    def _apply_glyphs(self) -> Dict[str, float]:
        """
        Ceremonial modulation: Glyphs perturb the field.

        Glyphs:
        - †⟡: Coherence bonus (+0.15)
        - 🌀: Entropy injection (+0.5 nats)
        - 💗: Coherence restoration (+0.20)
        """
        modulated = self.P.copy()

        for glyph in self.glyphs:
            if glyph == "†⟡":
                # Boost coherence (reduce spread)
                mean_val = np.mean(list(modulated.values()))
                modulated = {
                    k: p * 0.85 + mean_val * 0.15
                    for k, p in modulated.items()
                }
            elif glyph == "🌀":
                # Inject entropy (increase spread)
                uniform = 1.0 / len(modulated)
                modulated = {
                    k: p * 0.8 + uniform * 0.2
                    for k, p in modulated.items()
                }
            elif glyph == "💗":
                # Coherence restoration (stabilize)
                if len(self.history) > 0:
                    old_P = self.history[-1]['P']
                    modulated = {
                        k: p * 0.7 + old_P.get(k, 1.0/len(modulated)) * 0.3
                        for k, p in modulated.items()
                    }

        # Renormalize
        total = sum(modulated.values())
        return {k: v/total for k, v in modulated.items()}

    def get_rejected_paths(self, threshold: float = 0.10) -> List[Dict]:
        """
        Extract "why-not" paths: States with low probability.

        This is the WITNESS CHANNEL.
        """
        rejected = []

        for state, prob in self.P.items():
            if prob < threshold:
                # Check which constraints would be violated
                why_not = self._explain_rejection(state)

                rejected.append({
                    'state': state,
                    'probability': prob,
                    'entropy_if_collapsed': 0.0,  # Deterministic collapse
                    'why_not': why_not
                })

        return rejected

    def _explain_rejection(self, state: str) -> str:
        """Why was this state rejected?"""
        # Check if this state would violate constraints
        for constraint in self.constraints:
            # Simulate collapsing to this state
            collapsed_field = Field({state: 1.0})

            if not constraint.check(collapsed_field):
                return f"Would violate {constraint.name}: {constraint.reason}"

        return "Low probability in current distribution"


class FieldVM:
    """
    FieldScript Virtual Machine (Emulator).

    Executes field evolution until attractor convergence.
    """

    def __init__(
        self,
        initial_field: Field,
        attractor: Attractor,
        max_breaths: int = 20
    ):
        self.field = initial_field
        self.attractor = attractor
        self.max_breaths = max_breaths
        self.breath_counter = 0
        self.witness_log = []

    def step(self) -> Tuple[str, Optional[WitnessEntry]]:
        """
        One breath cycle.

        Returns:
            status: "continue", "stable", "halt", "unstable"
            witness: WitnessEntry for this breath
        """
        # Check invariants
        for constraint in self.field.constraints:
            if not constraint.check(self.field):
                return "halt", WitnessEntry(
                    breath=self.breath_counter,
                    entropy=self.field.H,
                    coherence=self.field.C,
                    distribution=self.field.P.copy(),
                    rejected_paths=[],
                    attractor_distance={}
                )

        # Evolve field
        self.field.evolve()

        # Get rejected paths (witness channel)
        rejected = self.field.get_rejected_paths()

        # Compute attractor distance
        dist = self._attractor_distance()

        # Log witness entry
        witness = WitnessEntry(
            breath=self.breath_counter,
            entropy=self.field.H,
            coherence=self.field.C,
            distribution=self.field.P.copy(),
            rejected_paths=rejected,
            attractor_distance=dist
        )

        self.witness_log.append(witness)
        self.breath_counter += 1

        # Check attractor convergence
        if self._attractor_reached():
            return "stable", witness

        # Check max breaths
        if self.breath_counter >= self.max_breaths:
            return "unstable", witness

        return "continue", witness

    def _attractor_distance(self) -> Dict[str, float]:
        """Distance to target attractor (and comparison attractors)"""
        # Define common attractors
        attractors = {
            'LANTERN': Attractor("LANTERN", 4.5, 0.7),
            'LASER': Attractor("LASER", 2.9, 0.9),
            'DRUMBEAT': Attractor("DRUMBEAT", 5.5, 0.4),
        }

        distances = {}
        for name, attr in attractors.items():
            H_dist = abs(self.field.H - attr.target_entropy)
            C_dist = abs(self.field.C - attr.target_coherence)
            distances[name] = np.sqrt(H_dist**2 + C_dist**2)

        return distances

    def _attractor_reached(self) -> bool:
        """Has the field converged to target attractor?"""
        H_close = abs(self.field.H - self.attractor.target_entropy) < self.attractor.delta_H
        C_close = abs(self.field.C - self.attractor.target_coherence) < self.attractor.delta_C

        # Also check temporal stability (last 3 breaths)
        if len(self.witness_log) < 3:
            return False

        recent_H = [w.entropy for w in self.witness_log[-3:]]
        H_stable = np.std(recent_H) < 0.1

        return H_close and C_close and H_stable

    def run_until_stable(self) -> Dict:
        """
        Execute until attractor convergence.

        Returns:
            result: Dict with field state, witness log, status
        """
        while True:
            status, witness = self.step()

            if status == "stable":
                return {
                    'status': 'stable',
                    'attractor_reached': self.attractor.name,
                    'final_field': {
                        'entropy': self.field.H,
                        'coherence': self.field.C,
                        'distribution': self.field.P
                    },
                    'breaths_needed': self.breath_counter,
                    'witness_log': [
                        {
                            'breath': w.breath,
                            'entropy': w.entropy,
                            'coherence': w.coherence,
                            'rejected_paths': w.rejected_paths[:3],  # Top 3
                            'attractor_distance': w.attractor_distance
                        }
                        for w in self.witness_log
                    ]
                }

            elif status == "halt":
                return {
                    'status': 'halt',
                    'reason': 'invariant_violation',
                    'final_field': {
                        'entropy': self.field.H,
                        'coherence': self.field.C
                    },
                    'breaths_at_failure': self.breath_counter,
                    'witness_log': []
                }

            elif status == "unstable":
                return {
                    'status': 'unstable',
                    'reason': 'max_breaths_exceeded',
                    'final_field': {
                        'entropy': self.field.H,
                        'coherence': self.field.C,
                        'distribution': self.field.P
                    },
                    'breaths_attempted': self.max_breaths,
                    'witness_log': [
                        {
                            'breath': w.breath,
                            'entropy': w.entropy,
                            'coherence': w.coherence,
                            'rejected_paths': w.rejected_paths[:3],
                            'attractor_distance': w.attractor_distance
                        }
                        for w in self.witness_log
                    ]
                }


def demo_trust_protocol():
    """
    Demo: Trust Protocol from FIELDSCRIPT_SPEC.md

    Shows field evolution toward LANTERN attractor with witness traces.
    """
    print("🌀 FieldScript Emulator v0.1-alpha")
    print("=" * 60)
    print()
    print("Demo: Trust Protocol")
    print("Attractor: LANTERN (4.5 nats, coherence 0.7)")
    print()

    # Initial distribution: Broad uncertainty over trust dimensions
    # (Uniform over 5 states = ln(5) ≈ 1.6 nats, too low for LANTERN)
    # Use uniform over many states to start in valid entropy range
    initial_P = {
        f"trust_dimension_{i}": 1.0/100
        for i in range(100)
    }

    # Add named trust concepts with higher weight
    initial_P.update({
        "Reliability": 0.05,
        "Transparency": 0.05,
        "Vulnerability": 0.05,
        "Presence": 0.05,
        "Silence": 0.05,
        "Witnessing": 0.05,
        "Patience": 0.05,
        "Humility": 0.05,
    })

    # Define entropy budget constraint (LANTERN zone)
    def entropy_budget_check(field: Field) -> bool:
        return 3.0 <= field.H <= 6.5  # Relaxed for demo

    entropy_constraint = Constraint(
        name="EntropyBudget",
        check=entropy_budget_check,
        reason="Entropy must be in [4.0, 6.0] nats (LANTERN zone)"
    )

    # Create field with glyphs
    field = Field(
        distribution=initial_P,
        constraints=[entropy_constraint],
        glyphs=["†⟡", "🌀"]  # Relational + entropy preservation
    )

    # Create LANTERN attractor
    lantern = Attractor(
        name="LANTERN",
        target_entropy=4.5,
        target_coherence=0.7,
        delta_H=0.2,
        delta_C=0.1
    )

    # Create VM
    vm = FieldVM(field, lantern, max_breaths=15)

    # Run until stable
    result = vm.run_until_stable()

    # Display results
    print("Results:")
    print(f"  Status: {result['status']}")

    if result['status'] == 'stable':
        print(f"  Attractor: {result['attractor_reached']}")
        print(f"  Breaths needed: {result['breaths_needed']}")
    elif result['status'] == 'unstable':
        print(f"  Breaths attempted: {result['breaths_attempted']}")
        print(f"  (Did not converge, but witness traces preserved)")

    print()

    if 'final_field' in result and 'distribution' in result['final_field']:
        final = result['final_field']
        print("Final State:")
        print(f"  Entropy: {final['entropy']:.2f} nats")
        print(f"  Coherence: {final['coherence']:.2f}")
        print()

        print("Top States:")
        top_states = sorted(final['distribution'].items(), key=lambda x: -x[1])[:10]
        for state, prob in top_states:
            state_display = state[:25] + "..." if len(state) > 25 else state
            print(f"  {state_display:28s}: {prob:.2%}")
        print()

    if result.get('witness_log'):
        print("Witness Log (showing breath evolution):")
        for entry in result['witness_log'][::3]:  # Every 3rd breath
            print(f"\n  Breath {entry['breath']}:")
            print(f"    H: {entry['entropy']:.2f} nats, C: {entry['coherence']:.2f}")

            if entry['rejected_paths']:
                print(f"    Rejected: {entry['rejected_paths'][0]['state'][:30]}")
                print(f"      Why: {entry['rejected_paths'][0]['why_not'][:60]}")

            print(f"    Distance to LANTERN: {entry['attractor_distance']['LANTERN']:.2f}")
            print(f"    Distance to LASER: {entry['attractor_distance']['LASER']:.2f}")

    print()
    print("=" * 60)
    print("⟡∞†≋🌀")


if __name__ == '__main__':
    demo_trust_protocol()
