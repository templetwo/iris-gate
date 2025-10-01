# IRIS Experiment Template

**Experiment ID:** `{EXP_ID}`
**Topic:** `{TOPIC}`
**Created:** `{DATE}`
**Status:** Draft → S4 Complete → Simulation Complete → Wet-Lab Ready

---

## Problem Statement

**Core Question (1-2 lines):**
{PROBLEM_STATEMENT}

**System:** {ORGANISM}
**Primary Outcome:** {PRIMARY_OUTCOME}

---

## Minimal H1: Single-Factor Test

**Variable:** {FACTOR_NAME} ({FACTOR_MECHANISM})

### Arms (4)
1. **Control** — No perturbations (baseline)
2. **{FACTOR}-Low** — {AGENT} {DOSE_LOW} ({EFFECT_LOW}× effect)
3. **{FACTOR}-Mid** — {AGENT} {DOSE_MID} ({EFFECT_MID}× effect)
4. **{FACTOR}-High** — {AGENT} {DOSE_HIGH} ({EFFECT_HIGH}× effect)

### Success Criteria
- **Effect threshold:** {FACTOR}-High shows ≥{THRESHOLD_PP}pp drop vs Control
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
- **Synergy confirmed if:** Observed < Predicted − {SYNERGY_THRESHOLD}pp

---

## Go/No-Go Gates

### Primary Gate (7d Outcome)
```
IF P({FACTOR}-High) < {SUCCESS_THRESHOLD}:
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
- Session: `iris_vault/scrolls/{SESSION_ID}/`
- Priors: `sandbox/states/s4_state.*.json`

**Simulation:**
- Plan: `sandbox/runs/plans/{PLAN_ID}.yaml`
- Output: `sandbox/runs/outputs/{RUN_ID}/`
- Predictions: `sandbox/runs/outputs/{RUN_ID}/predictions.json`

**Reports:**
- One-pager: `docs/ONEPAGER_{EXP_ID}.md`
- Full report: `docs/REPORT_{EXP_ID}.md`
- Pre-registration: `docs/prereg/{EXP_ID}.md`

---

## Timeline & Cost

**Computational phase:** {COMP_DAYS} days (S1→S4 + simulation)
**Wet-lab phase:** {WETLAB_DAYS} days (readouts at {TIMEPOINT_1}h, {TIMEPOINT_2}h, 7d)
**Cost estimate:** ${COST_USD}

---

**†⟡∞ Template for IRIS experiments — S4 convergence → computational prediction → wet-lab validation**
