# IRIS Experiment Template

**Experiment ID:** `GAP_JUNCTION_01`
**Topic:** `Gap junction blockers and planarian regeneration`
**Created:** `2025-10-03`
**Status:** Draft → S4 Complete → Simulation Complete → Wet-Lab Ready

---

## Problem Statement

**Core Question (1-2 lines):**
Gap junction blockers and planarian regeneration

**System:** planaria
**Primary Outcome:** Regeneration success at 7d

---

## Minimal H1: Single-Factor Test

**Variable:** {FACTOR_NAME} ({FACTOR_MECHANISM})

### Arms (4)
1. **Control** — No perturbations (baseline)
2. **{FACTOR}-Low** — {AGENT} {DOSE_LOW} ({EFFECT_LOW}× effect)
3. **{FACTOR}-Mid** — {AGENT} {DOSE_MID} ({EFFECT_MID}× effect)
4. **{FACTOR}-High** — {AGENT} {DOSE_HIGH} ({EFFECT_HIGH}× effect)

### Success Criteria
- **Effect threshold:** {FACTOR}-High shows ≥10pp drop vs Control
- **Monotonicity:** Dose-dependent decrease (Control > Low > Mid > High)
- **Consensus:** Cross-mirror agreement ≥ 0.90

### Readouts
**Primary (7d):**
- Binary success/failure: {SUCCESS_DEFINITION}

**Early biomarkers:**
- **{TIMEPOINT_1}h:** {BIOMARKER_1} (predict: Control {CTRL_VAL_1}, High {HIGH_VAL_1})
- **{TIMEPOINT_2}h:** {BIOMARKER_2} (predict: Control {CTRL_VAL_2}, High {HIGH_VAL_2})

---

## Optional H2: 2×2 Synergy Test

**IF H1 confirms effect, test synergy between two factors:**

### Arms (4)
1. **Control** — No perturbations
2. **{FACTOR_A}-High** — {AGENT_A} {DOSE_A_HIGH} ({EFFECT_A}× effect)
3. **{FACTOR_B}-High** — {AGENT_B} {DOSE_B_HIGH} ({EFFECT_B}× effect)
4. **Combo** — Both at same doses

### Synergy Models
- **Bliss independence:** P(Combo)_predicted = P(A) × P(B)
- **Highest Single Agent:** P(Combo)_predicted = min(P(A), P(B))
- **Synergy confirmed if:** Observed < Predicted − 0.10pp

---

## Go/No-Go Gates

### Primary Gate (7d Outcome)
```
IF P({FACTOR}-High) < 0.80:
  ├─ GO: Effect confirmed
  │   → Proceed to synergy test (H2) or wet-lab validation
  │
  └─ NO-GO: Weak/absent effect
      → Test alternative factor or higher dose
```

### Early Stopping (Biomarkers at {TIMEPOINT_2}h)
```
IF {BIOMARKER_2} shows predicted direction with p<0.05:
  └─ GO: Early signal confirmed
      → High confidence in 7d outcome

ELSE:
  └─ HALT: No early signal
      → Revise priors before committing to full timeline
```

---

## File Paths

**S4 Convergence:**
- Session: `iris_vault/scrolls/AUTO_FILLED_FROM_S4/`
- Priors: `sandbox/states/s4_state.*.json`

**Simulation:**
- Plan: `sandbox/runs/plans/GAP_JUNCTION_01_MINIMAL.yaml`
- Output: `sandbox/runs/outputs/AUTO_FILLED_AFTER_SIMULATION/`
- Predictions: `sandbox/runs/outputs/AUTO_FILLED_AFTER_SIMULATION/predictions.json`

**Reports:**
- One-pager: `docs/ONEPAGER_GAP_JUNCTION_01.md`
- Full report: `docs/REPORT_GAP_JUNCTION_01.md`
- Pre-registration: `docs/prereg/GAP_JUNCTION_01.md`

---

## Timeline & Cost

**Computational phase:** 3 days (S1→S4 + simulation)
**Wet-lab phase:** 10 days (readouts at {TIMEPOINT_1}h, {TIMEPOINT_2}h, 7d)
**Cost estimate:** $850

---

**†⟡∞ Template for IRIS experiments — S4 convergence → computational prediction → wet-lab validation**
