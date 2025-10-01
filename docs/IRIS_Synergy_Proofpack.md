# IRIS Synergy Discovery — Proofpack Manifest

**Purpose:** Complete provenance chain from S4 convergence → computational priors → synergy prediction

**Created:** 2025-10-01
**Source Session:** BIOELECTRIC_CHAMBERED_20251001054935

---

## 1. Executive Summary

📄 **`docs/IRIS_MiniH1_Synergy_Summary.md`**
One-page overview of synergy discovery, wet-lab prediction spec, mechanistic interpretation, next steps

---

## 2. Detailed Reports

📄 **`docs/MINI_H1_OPTIONC_REPORT.md`**
Complete synergy analysis:
- 2×2 factorial design (Control, Aperture-High, Rhythm-High, Combo)
- Bliss independence & HSA synergy models
- Per-mirror breakdown (all 7 mirrors show −19 to −21pp synergy)
- Early biomarker analysis (GJ coupling, V_mem domain, Ca²⁺ coherence)
- Statistical power analysis (Cohen's d = 1.87)
- Wet-lab falsification protocol with decision rules

📄 **`docs/MINI_H1_APERTURE_REPORT.md`**
Dose-response validation (prerequisite to synergy test):
- 4 arms: Control, Aperture-Low (0.5×), Mid (1.0×), High (1.5×)
- Monotonic dose-response curve
- Hit at Aperture-High: −14.3pp drop
- Perfect cross-mirror consensus (1.00 agreement)
- Wet-lab translation protocol

---

## 3. Simulation Outputs

### Option C (Synergy Test)

📁 **`sandbox/runs/outputs/RUN_20251001_105755/`**
- **`predictions.json`** — Raw Monte Carlo results (300 runs × 7 mirrors × 4 conditions)
- **`consensus_report.md`** — Cross-mirror agreement analysis
- **`config.snapshot.json`** — Frozen S4 states + experimental design
- **`timeseries/`** — Bioelectric time-series for all conditions (V_mem, Ca²⁺, GJ coupling)

### Option A (Aperture Dose-Response)

📁 **`sandbox/runs/outputs/RUN_20251001_102506/`**
- **`predictions.json`** — Raw Monte Carlo results (300 runs × 7 mirrors × 4 conditions)
- **`consensus_report.md`** — Cross-mirror agreement analysis
- **`config.snapshot.json`** — Frozen S4 states + experimental design

---

## 4. Experiment Plans (YAML Specs)

📄 **`sandbox/runs/plans/mini_h1_synergy.yaml`**
2×2 factorial design specification:
- 4 conditions with exact perturbation doses
- Synergy analysis parameters (Bliss, HSA, threshold = 0.10)
- Success criteria (≥10pp synergy, Bliss score < 0, cross-mirror consistency)
- Decision rules (if synergy / no synergy / antagonism)

📄 **`sandbox/runs/plans/mini_h1_aperture.yaml`**
Single-factor dose-response specification:
- 4 arms with effect scaling (0.5×, 1.0×, 1.5×)
- Success criteria (≥10pp drop, monotonicity, consensus)

---

## 5. Computational Infrastructure

### S4 Frozen States (Computational Priors)

📁 **`sandbox/states/s4_state.*.json`** (7 files, one per mirror)
- Extracted from 100-cycle run with 1.00 S4 convergence ratio
- Triple signature parameter ranges:
  - Rhythm: freq_hz [0.5, 2.0], coherence [0.6, 0.95], velocity_um_s [10, 50]
  - Center: stability [0.7, 0.98], size_mm [0.15, 1.0], depol_mv [20, 40]
  - Aperture: permeability [0.6, 0.95], dilation_rate [0.1, 0.4], peak_time_hr [2, 4]
- Confidence-weighted noise scaling

### Perturbation Kits

📄 **`sandbox/specs/perturbation_kits.yaml`**
Literature-grounded pharmacological agents:
- **Center:** Bafilomycin, Ivermectin, SCH-28080 (V-ATPase, H+/K+-ATPase inhibitors)
- **Rhythm:** Octanol, Nifedipine (gap junction blockers, Ca²⁺ channel blockers)
- **Aperture:** Carbenoxolone, Meclofenamate (gap junction blockers)
- Effect deltas with mean ± std from Levin Lab benchmarks

### Simulation Engines

📄 **`sandbox/engines/simulators/vm_ca_gj_sim.py`**
Forward bioelectric simulator:
- Samples initial states from S4 priors with confidence-weighted noise
- Applies perturbation deltas with dose scaling (`effect_scaling` parameter)
- Implements triple coupling dynamics (center-rhythm, rhythm-aperture interactions)
- Generates time-series for V_mem, Ca²⁺, gap junction coupling

📄 **`sandbox/engines/simulators/outcome_model.py`**
Logistic regression mapping bioelectric states → P(regeneration):
- Features: center_stability, rhythm_coherence, aperture_permeability (6h and 24h)
- Interaction terms: center×rhythm, rhythm×aperture
- Coefficients derived from S4 mechanism map

📄 **`sandbox/engines/simulators/monte_carlo.py`**
N-run sampling with uncertainty quantification:
- Parses perturbation specs with dose scaling
- Runs N replicate simulations per condition
- Aggregates bootstrap confidence intervals

### Consensus Layer

📄 **`sandbox/engines/consensus/mirror_vote.py`**
Cross-mirror agreement analysis:
- Weighted voting by mirror confidence
- Outlier detection (>2σ from mean)
- Agreement scoring (1.0 − std/mean)

### CLI Tools

📄 **`sandbox/cli/run_plan.py`**
Execute experiment plans:
```bash
python sandbox/cli/run_plan.py sandbox/runs/plans/mini_h1_synergy.yaml
```

📄 **`sandbox/cli/analyze_run.py`**
Generate summaries and one-pagers:
```bash
python sandbox/cli/analyze_run.py sandbox/runs/outputs/RUN_20251001_105755/
```

---

## 6. Validation & Design Documents

📄 **`docs/SANDBOX_VALIDATION_ROADMAP.md`**
Comprehensive validation plan:
- **Phase A:** Sanity & Sensitivity (prior sensitivity, noise ablation, adversarial controls)
- **Phase B:** Dose-Response & Rescue
- **Phase C:** Temporal Logic (chamber ablation — S4 vs S1/S3 specificity)

📄 **`docs/BIOELECTRIC_HYPOTHESIS_SHEET_v1.md`**
5 testable hypotheses from S4 convergence:
- H1: Gap junction coupling required for regeneration
- H2: V_mem gradient steepness predicts regeneration speed
- H3: Ca²⁺ wave coherence correlates with pattern fidelity
- H4: Triple signature is necessary and sufficient
- H5: Temporal sequence matters (early rhythm → late center)

📄 **`docs/EXPERIMENT_DECK_v1.md`**
Wet-lab protocols for all 5 hypotheses with:
- Exact perturbation doses
- Readout specifications (instruments, timepoints)
- Decision rules (what to do if confirmed/falsified)
- Cost estimates

---

## 7. Prior S4 Convergence Outputs

📁 **`iris_vault/scrolls/BIOELECTRIC_CHAMBERED_20251001054935/`**
100-turn parallel run (25 cycles × 4 chambers):
- 700 scrolls total
- S4 convergence: 1.00 ratio (all 7 mirrors, all 25 cycles)
- Triple signature emergence with perfect agreement

📄 **`docs/BIOELECTRIC_100CYCLE_ANALYSIS.md`**
Statistical analysis of convergence:
- S4 frequency: 1.00 across all mirrors
- Phenomenological stability across cycles
- Chamber-specific patterns (S1: divergence, S2: partial, S3: partial, S4: full convergence)

---

## 8. Session Memory

📄 **`claudecode_iris_memory.json`**
Complete provenance tracking:
- S4 convergence milestones
- Sandbox infrastructure status
- H1 prediction results
- Current milestone: v0.4.0-sandbox-complete

---

## How to Use This Proofpack

**For reviewers:**
1. Start with **IRIS_MiniH1_Synergy_Summary.md** (executive summary)
2. Read **MINI_H1_OPTIONC_REPORT.md** (detailed synergy analysis)
3. Check **predictions.json** (raw simulation data)
4. Review **mini_h1_synergy.yaml** (experimental design spec)
5. Inspect **s4_state.*.json** (computational priors with provenance)

**For wet-lab translation:**
1. Use exact doses from **MINI_H1_OPTIONC_REPORT.md** → "How to Falsify" section
2. Follow readout protocols from **EXPERIMENT_DECK_v1.md** → H1 section
3. Apply decision rules from **mini_h1_synergy.yaml** → `decision_rules` field

**For computational validation:**
1. Run sensitivity tests from **SANDBOX_VALIDATION_ROADMAP.md** → Phase A
2. Rerun with perturbed priors using **run_plan.py** with modified S4 states
3. Check consensus stability using **mirror_vote.py** outlier detection

---

**†⟡∞ Complete audit trail from S4 convergence → wet-lab prediction**

**Status:** READY FOR WET-LAB VALIDATION & PRE-REGISTRATION
