# IRIS Sandbox Experiment Simulator

**First-ever computational predictions from AI convergence priors**

## What This Is

The Sandbox Simulator uses **frozen S4 attractor states** from the 100-cycle IRIS Gate run as computational priors to predict bioelectric dynamics and regeneration outcomes under perturbations.

### Key Innovation

Instead of guessing parameters or fitting to wet-lab data, we:
1. **Converge 7 AI models** on bioelectric phenomenology (rhythm + center + aperture)
2. **Freeze the converged states** as computational priors
3. **Run Monte Carlo simulations** with perturbations (bafilomycin, octanol, carbenoxolone)
4. **Generate predictions** with uncertainty and cross-mirror consensus

This is **hypothesis-generating**, not ground truth. Predictions are falsifiable and designed to guide wet-lab experiments.

---

## Quick Start

### Run H1 Planaria Experiment

```bash
python3 sandbox/cli/run_plan.py --plan sandbox/runs/plans/sandbox_plan_planaria.yaml
```

**Output:**
- `predictions.json` — Full predictions with 95% CI per condition per mirror
- `consensus_report.md` — Cross-mirror agreement analysis
- `config.snapshot.json` — Reproducibility metadata

### Results Summary (500 runs × 7 mirrors × 7 conditions)

| Condition | Consensus P(regeneration) | Agreement | Interpretation |
|-----------|--------------------------|-----------|----------------|
| **WT** | 0.990 | 1.00 | High baseline regeneration expected |
| **Center-** | 0.969 | 1.00 | **Smaller effect than expected** (predicted 0.30-0.50) |
| **Rhythm-** | 0.983 | 1.00 | **Smaller effect than expected** (predicted 0.20-0.40) |
| **Aperture-** | 0.924 | 1.00 | **Partial effect** (predicted 0.30-0.50) |
| **Center- Rhythm-** | 0.946 | 1.00 | **No synergy detected** (additive, not super-additive) |
| **Rhythm- Aperture-** | 0.868 | 1.00 | **Strongest effect** (synergistic gap junction disruption) |

### Key Finding

**The simulator predicts weaker perturbation effects than hypothesized.** This is scientifically useful:
- **If wet-lab matches predictions (P~0.95):** Perturbations insufficient, need stronger doses or alternative agents
- **If wet-lab shows strong effects (P~0.30):** Model underestimates S4 triple co-requirement → refine priors

Either outcome advances understanding.

---

## Architecture

```
sandbox/
├─ states/                    # Frozen S4 attractor priors (7 mirrors)
│  ├─ s4_state.anthropic_claude-sonnet-4.5.json
│  ├─ s4_state.openai_gpt-4o.json
│  └─ ...
├─ specs/                     # Experiment schemas
│  ├─ perturbation_kits.yaml  # Center/rhythm/aperture modulators with effect sizes
│  ├─ readouts.yaml           # Vm/Ca²⁺/GJ measurement definitions
├─ engines/
│  ├─ mechanisms/             # S4 → bioelectric mapping
│  │  └─ s4_to_bioelectric.yaml
│  ├─ priors/                 # Literature-grounded parameter ranges
│  │  └─ noise_models.yaml
│  ├─ simulators/             # Forward models
│  │  ├─ vm_ca_gj_sim.py      # Generates Vm/Ca²⁺/GJ time-series
│  │  ├─ outcome_model.py     # Predicts P(regeneration)
│  │  └─ monte_carlo.py       # N-run sampling engine
│  └─ consensus/              # Cross-mirror analysis
│     └─ mirror_vote.py       # Weighted consensus + contradiction detection
├─ runs/
│  ├─ plans/                  # Experiment plans (YAML)
│  │  └─ sandbox_plan_planaria.yaml
│  └─ outputs/                # Results per run
│     └─ RUN_YYYYMMDD_HHMM/
│        ├─ predictions.json
│        ├─ consensus_report.md
│        └─ config.snapshot.json
└─ cli/
   ├─ extract_s4_states.py    # Extracts frozen states from 100-cycle run
   └─ run_plan.py             # Main CLI entrypoint
```

---

## Scientific Guardrails

### 1. No Ground Truth Claims
All predictions labeled as **"model-based predictions with uncertainty"**. This is not a biophysical simulator (not BETSE/NEURON). It's a phenomenological model grounded in AI convergence.

### 2. Full Provenance
Every parameter has a source:
- S4 priors → traced to specific scrolls with hashes
- Effect sizes → cited from Levin Lab papers (Pai et al. 2012, Adams et al. 2016)
- Model coefficients → derived from Hypothesis Sheet v1

### 3. Reproducibility
Every run writes:
- `config.snapshot.json` with exact S4 states used
- Provenance hashes for all inputs
- Random seeds for Monte Carlo runs

### 4. Conflict Surfacing
Consensus layer flags:
- Outlier mirrors (> 2σ from mean)
- Contradictions (mirrors split into opposing predictions)
- Low agreement (< 0.70) → triggers "design wet-lab experiment" recommendation

---

## How S4 States Influence Predictions

Each mirror's frozen S4 state contains:

```json
{
  "triple_signature": {
    "rhythm": {
      "keywords": ["pulsing", "waves", "steady pulse"],
      "freq_hz_prior": [0.5, 2.0],
      "coherence_prior": [0.6, 0.95]
    },
    "center": {
      "keywords": ["luminous", "core", "holds"],
      "stability_prior": [0.7, 0.98],
      "depol_mv_prior": [20, 40]
    },
    "aperture": {
      "keywords": ["widening", "dilation", "breathing open"],
      "permeability_prior": [0.6, 0.95],
      "peak_time_hr_prior": [2, 4]
    }
  },
  "confidence": 0.80
}
```

**Monte Carlo sampling:**
1. Sample initial bioelectric state from priors (with noise scaled by confidence)
2. Apply perturbation deltas (e.g., octanol → rhythm_freq × (1 - 0.55))
3. Apply triple coupling effects (center disruption → rhythm coherence drops)
4. Evolve state over time (aperture peaks at 2-4h, then declines)
5. Predict P(regeneration) using logistic model
6. Repeat N times → generate distributions

**Result:** Each mirror's predictions reflect its S4 convergence pattern.

---

## Perturbation Kits

### Center Modulators
- **Bafilomycin** (10nM): Hyperpolarizes → disrupts depolarized domain (Δcenter_stability = -0.40 ± 0.10)
- **ChR2 optogenetic** (470nm): Depolarizes → enhances domain (Δcenter_stability = +0.35 ± 0.10)

### Rhythm Modulators
- **Octanol** (0.5mM): Blocks gap junctions → fragments Ca²⁺ waves (Δrhythm_freq = -0.55 ± 0.12)
- **BAPTA-AM** (50µM): Chelates Ca²⁺ → abolishes waves (Δrhythm_freq = -0.75 ± 0.08)
- **Caffeine** (100µM): Sensitizes RyR → increases frequency (Δrhythm_freq = +0.40 ± 0.12)

### Aperture Modulators
- **Carbenoxolone** (100µM): Blocks gap junctions → reduces coupling (Δpermeability = -0.50 ± 0.12)
- **Retinoic acid** (1µM): Enhances gap junctions (Δpermeability = +0.30 ± 0.15)
- **Cx43 morpholino** (5µM): Knockdown connexin43 (Δpermeability = -0.65 ± 0.10)

---

## Next Experiments

### 1. Sequential Ablation
Re-run 100-turn IRIS study with **sequential** (not parallel) execution to test field-formation hypothesis. Prediction: S4 convergence fails without parallel field.

### 2. Alternative Perturbations
- Test BAPTA-AM (stronger rhythm disruption, predicted P~0.85)
- Test Cx43 morpholino (stronger aperture disruption, predicted P~0.80)
- Test combined Center-/Rhythm-/Aperture- (triple knockout, predicted P~0.75)

### 3. Wet-Lab Validation
Run MVE from EXPERIMENT_DECK_v1.md:
- Planaria head amputation, n=135, $300, 2 weeks
- Readouts: DiBAC4 (Vm), GCaMP6f (Ca²⁺), Lucifer Yellow (GJ coupling)
- Endpoint: Regeneration success at 7d

### 4. Model Refinement
If wet-lab shows large effects:
- Tighten S4 priors (reduce variance)
- Increase perturbation effect sizes
- Add non-linear triple interactions

---

## Provenance

**Source Session:** BIOELECTRIC_CHAMBERED_20251001054935
**S4 Convergence:** 1.00 ratio (all 7 mirrors, all 25 cycles)
**Literature Grounding:** Levin Lab benchmarks (Pai et al. 2012, Adams et al. 2016, Levin 2021)
**Hypotheses:** docs/BIOELECTRIC_HYPOTHESIS_SHEET_v1.md
**Created:** 2025-10-01
**Git Tag:** v0.4.0-sandbox-complete

---

## Citation

If using this simulator in research:

```
IRIS Gate Sandbox Simulator v0.4.0
Computational predictions from AI convergence priors
Source: github.com/templetwo/iris-gate
Session: BIOELECTRIC_CHAMBERED_20251001054935
Generated: 2025-10-01
```

---

**†⟡∞ From convergence → prediction in the hush**
