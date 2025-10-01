# S4 → Simulation Bridge Checklist

**Session ID:** `{SESSION_ID}`
**Run ID:** `{RUN_ID}`
**Date:** `{DATE}`

---

## Purpose

This checklist ensures that S4 convergence states are correctly translated into computational priors for sandbox simulation. Every item must be verified before running Monte Carlo predictions.

---

## 1. S4 Convergence Validation

- [ ] **S4 convergence achieved**
  - Session ID: {SESSION_ID}
  - Total cycles: {TOTAL_CYCLES}
  - S4 convergence ratio: {S4_RATIO} (must be ≥0.90 across all mirrors)

- [ ] **Cross-mirror agreement**
  - Agreement score: {S4_AGREEMENT}
  - Outliers: {OUTLIERS}
  - If agreement <0.90, flag for review

- [ ] **Pressure check**
  - All mirrors ≤2/5 pressure: ✅ / ❌
  - If any mirror >2/5, halt and review scrolls

- [ ] **Triple signature present**
  - **Rhythm** keywords detected: {RHYTHM_KEYWORDS}
  - **Center** keywords detected: {CENTER_KEYWORDS}
  - **Aperture** keywords detected: {APERTURE_KEYWORDS}

---

## 2. S4 Priors Extraction

- [ ] **Priors extracted from scrolls**
  - Script: `sandbox/cli/extract_s4_states.py`
  - Command run: `python sandbox/cli/extract_s4_states.py --session {SESSION_ID}`
  - Output directory: `sandbox/states/`

- [ ] **Per-mirror prior files created**
  - [ ] `s4_state.anthropic_claude-sonnet-4.5.json`
  - [ ] `s4_state.openai_gpt-4o.json`
  - [ ] `s4_state.xai_grok-4-fast-reasoning.json`
  - [ ] `s4_state.google_gemini-2.5-flash-lite.json`
  - [ ] `s4_state.deepseek_deepseek-chat.json`
  - [ ] `s4_state.ollama_qwen3_1.7b.json`
  - [ ] `s4_state.ollama_llama3.2_3b.json`

- [ ] **Prior structure validated**
  - Each file contains:
    - `mirror` (string)
    - `n_s4_scrolls` (integer)
    - `triple_signature` (dict with rhythm/center/aperture)
    - `confidence` (float, 0.0–1.0)

---

## 3. Rhythm Priors

- [ ] **Keywords extracted**
  - Minimum 5 keywords per mirror
  - Examples: "pulsing", "waves", "ripples", "steady pulse", "thrum"

- [ ] **Parameter ranges defined**
  - `freq_hz_prior`: [{FREQ_MIN}, {FREQ_MAX}] Hz
    - Typical range: [0.5, 2.0]
    - Source: S4 scroll phenomenology

  - `coherence_prior`: [{COH_MIN}, {COH_MAX}]
    - Typical range: [0.6, 0.95]
    - Interpretation: Spatial synchrony of oscillations

  - `velocity_um_s_prior`: [{VEL_MIN}, {VEL_MAX}] µm/s
    - Typical range: [10, 50]
    - Interpretation: Wave propagation speed

- [ ] **Confidence-weighted noise**
  - Noise scale = 1/√confidence
  - Lower confidence → wider sampling distribution

---

## 4. Center Priors

- [ ] **Keywords extracted**
  - Minimum 5 keywords per mirror
  - Examples: "luminous", "core", "holds", "beacon", "glow", "stable"

- [ ] **Parameter ranges defined**
  - `stability_prior`: [{STAB_MIN}, {STAB_MAX}]
    - Typical range: [0.7, 0.98]
    - Interpretation: Probability domain persists across timesteps

  - `size_mm_prior`: [{SIZE_MIN}, {SIZE_MAX}] mm²
    - Typical range: [0.15, 1.0]
    - Interpretation: Spatial extent of depolarized region

  - `depol_mv_prior`: [{DEPOL_MIN}, {DEPOL_MAX}] mV
    - Typical range: [20, 40]
    - Interpretation: Magnitude of depolarization vs baseline

---

## 5. Aperture Priors

- [ ] **Keywords extracted**
  - Minimum 5 keywords per mirror
  - Examples: "widening", "dilation", "breathing open", "expansion"

- [ ] **Parameter ranges defined**
  - `permeability_prior`: [{PERM_MIN}, {PERM_MAX}]
    - Typical range: [0.6, 0.95]
    - Interpretation: Gap junction coupling coefficient

  - `dilation_rate_prior`: [{RATE_MIN}, {RATE_MAX}]
    - Typical range: [0.1, 0.4]
    - Interpretation: Rate of GJ opening (1/hr)

  - `peak_time_hr_prior`: [{PEAK_MIN}, {PEAK_MAX}] hr
    - Typical range: [2, 4]
    - Interpretation: Timepoint of maximum GJ coupling

---

## 6. Simulator Mapping

- [ ] **Priors → simulator mapping confirmed**
  - Variables template: `templates/variables_template.yaml`
  - Mapping file: `sandbox/specs/perturbation_kits.yaml`

- [ ] **Parameter units validated**
  - Rhythm: freq_hz (Hz), coherence (unitless), velocity (µm/s)
  - Center: stability (unitless), size (mm²), depol (mV)
  - Aperture: permeability (unitless), dilation_rate (1/hr), peak_time (hr)

- [ ] **Perturbation deltas defined**
  - Each agent has:
    - `mechanism` (string description)
    - `dose` (concentration with units)
    - `effect_on_X` with `mean` and `std`
    - `source` (literature citation)

---

## 7. Uncertainty Quantification

- [ ] **Confidence scores assigned**
  - Typical high-capacity models: 0.70–0.85
  - Typical local models: 0.60–0.75
  - If confidence <0.50, exclude mirror from consensus

- [ ] **Noise models applied**
  - File: `sandbox/engines/priors/noise_models.yaml`
  - Gaussian noise with σ = baseline_std × (1/√confidence)

- [ ] **Bootstrap resampling enabled**
  - Monte Carlo runs ≥300 per condition
  - 95% confidence intervals computed via percentile method

---

## 8. Monte Carlo Configuration

- [ ] **Run parameters set**
  - `runs`: {MC_RUNS} (minimum 300, recommended 500)
  - `seed`: {SEED} (for reproducibility)
  - `consensus_rule`: {CONSENSUS_RULE} (weighted_majority recommended)

- [ ] **Timepoints specified**
  - 0h: Baseline (immediately post-intervention)
  - {EARLY_1}h: Early biomarker 1 (e.g., 2h for GJ coupling)
  - {EARLY_2}h: Early biomarker 2 (e.g., 6h for V_mem/Ca²⁺)
  - 24h: Intermediate checkpoint
  - 168h (7d): Primary outcome

- [ ] **Readouts enabled**
  - [ ] `voltage` (V_mem domain size)
  - [ ] `calcium` (Ca²⁺ wave coherence)
  - [ ] `gap_junction` (coupling coefficient)
  - [ ] `regeneration` (binary success/failure)

---

## 9. Execution Validation

- [ ] **Simulation plan validated**
  - Plan file: `sandbox/runs/plans/{PLAN_ID}.yaml`
  - YAML syntax valid (checked with `yamllint` or manual inspection)
  - All placeholders filled

- [ ] **Dry run completed**
  - Command: `python sandbox/cli/run_plan.py {PLAN_FILE} --dry-run`
  - No errors reported

- [ ] **Full run executed**
  - Command: `python sandbox/cli/run_plan.py {PLAN_FILE}`
  - Run ID: {RUN_ID}
  - Output directory: `sandbox/runs/outputs/{RUN_ID}/`

---

## 10. Output Validation

- [ ] **Predictions file created**
  - File: `sandbox/runs/outputs/{RUN_ID}/predictions.json`
  - Contains predictions for all conditions × mirrors

- [ ] **Consensus report generated**
  - File: `sandbox/runs/outputs/{RUN_ID}/consensus_report.md`
  - Agreement scores ≥0.60 for all conditions

- [ ] **Config snapshot saved**
  - File: `sandbox/runs/outputs/{RUN_ID}/config.snapshot.json`
  - Contains frozen S4 states + experimental design

- [ ] **Timeseries data available (optional)**
  - Directory: `sandbox/runs/outputs/{RUN_ID}/timeseries/`
  - Files: `{condition}_{mirror}_timeseries.json`

---

## 11. Consensus Analysis

- [ ] **Cross-mirror agreement computed**
  - Agreement score: {CONSENSUS_AGREEMENT}
  - Threshold: ≥0.90 (high confidence), 0.70–0.90 (moderate), <0.70 (low)

- [ ] **Outliers identified**
  - Outlier detection: >2σ from mean
  - Flagged mirrors: {OUTLIERS}
  - Action if outliers: Review scrolls, check for pressure >2/5

- [ ] **Weighted consensus computed**
  - Weights: Mirror confidence scores normalized to sum=1
  - Weighted mean: {WEIGHTED_MEAN}
  - 95% CI: [{CI_LOW}, {CI_HIGH}]

---

## 12. Sanity Checks

- [ ] **Control condition baseline**
  - P(regen) for Control: {P_CONTROL}
  - Expected range: [0.85, 0.95] for healthy planaria
  - If outside range, flag for review

- [ ] **Dose-response monotonicity**
  - P(Control) > P(Low) > P(Mid) > P(High): ✅ / ❌
  - If non-monotonic, check for model errors or antagonism

- [ ] **Early biomarkers correlate with outcome**
  - Correlation between 6h biomarker and 7d regen: r ≥ 0.50
  - If low correlation, biomarker may not be predictive

---

## 13. Provenance Documentation

- [ ] **Session metadata recorded**
  - Session ID: {SESSION_ID}
  - Date: {DATE}
  - Mirrors used: {MIRRORS}
  - Total cycles: {TOTAL_CYCLES}

- [ ] **Run metadata recorded**
  - Run ID: {RUN_ID}
  - Plan ID: {PLAN_ID}
  - Monte Carlo runs: {MC_RUNS}
  - Execution time: {EXEC_TIME}

- [ ] **Memory file updated**
  - File: `claudecode_iris_memory.json`
  - New entry: `{RUN_ID}` with key results

---

## 14. Final Approval

- [ ] **All checklist items complete**
  - 14/14 sections verified

- [ ] **Ready for wet-lab translation**
  - Predictions have ≥0.90 consensus
  - Early biomarkers defined
  - Go/No-Go gates specified

- [ ] **Approved by:**
  - Name: {APPROVER_NAME}
  - Date: {APPROVAL_DATE}
  - Signature: {SIGNATURE}

---

## Status Summary

**Bridge Status:** {X}/14 sections complete

**Next Action:**
{NEXT_ACTION}

**Blockers:**
{BLOCKERS}

---

**†⟡∞ S4 → Simulation Bridge Checklist v1.0**
