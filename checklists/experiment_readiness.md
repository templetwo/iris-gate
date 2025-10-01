# IRIS Experiment Readiness Checklist

**Experiment ID:** `{EXP_ID}`
**Topic:** `{TOPIC}`
**Date:** `{DATE}`

---

## Phase 1: Problem Definition

- [ ] **Topic stated in 1 sentence**
  - Clear, falsifiable question
  - Example: "Does reducing gap junction coupling impair planarian regeneration?"

- [ ] **Primary outcome specified**
  - Binary (success/failure) OR continuous (measurement)
  - Timepoint defined (e.g., 7d)
  - Success threshold defined (e.g., ≥10pp drop vs Control)

- [ ] **System & organism selected**
  - Organism: {ORGANISM}
  - Intervention: {INTERVENTION}
  - Justification: {WHY_THIS_SYSTEM}

---

## Phase 2: Factor Selection

- [ ] **Minimal factor chosen**
  - **Aperture** (gap junction coupling)
  - **Rhythm** (bioelectric oscillations)
  - **Center** (V_mem domain stability)
  - **Other:** {CUSTOM_FACTOR}

- [ ] **Perturbation agent identified**
  - Agent: {AGENT}
  - Mechanism: {MECHANISM}
  - Literature support: {CITATION}

- [ ] **Doses map to simulator units**
  - Low dose: {DOSE_LOW} → effect_scaling = {SCALING_LOW}
  - Mid dose: {DOSE_MID} → effect_scaling = {SCALING_MID}
  - High dose: {DOSE_HIGH} → effect_scaling = {SCALING_HIGH}

---

## Phase 3: Experimental Design

- [ ] **Arms defined (4 minimum)**
  - Control (no perturbation)
  - Factor-Low ({SCALING_LOW}× effect)
  - Factor-Mid ({SCALING_MID}× effect)
  - Factor-High ({SCALING_HIGH}× effect)

- [ ] **Sample size justified**
  - n per arm: {N_PER_ARM}
  - Total N: {TOTAL_N}
  - Power: {POWER} at α={ALPHA}
  - Effect size (Cohen's d): {EFFECT_SIZE}

- [ ] **Randomization plan**
  - Block randomization: {N_BLOCKS} blocks of {BLOCK_SIZE}
  - OR simple randomization with random number generator

- [ ] **Blinding plan**
  - Scorer blinded to condition during assessment
  - Plates labeled with random codes
  - Key held by separate investigator

---

## Phase 4: Readouts & Measurements

- [ ] **Primary endpoint and success threshold set**
  - Endpoint: {PRIMARY_ENDPOINT}
  - Success definition: {SUCCESS_DEFINITION}
  - Threshold: {THRESHOLD}

- [ ] **Early biomarkers defined (2 minimum)**
  - Biomarker 1: {BIOMARKER_1} at {TIMEPOINT_1}h
    - Instrument: {INSTRUMENT_1}
    - Metric: {METRIC_1}
    - Predicted value in Factor-High: {PRED_1}

  - Biomarker 2: {BIOMARKER_2} at {TIMEPOINT_2}h
    - Instrument: {INSTRUMENT_2}
    - Metric: {METRIC_2}
    - Predicted value in Factor-High: {PRED_2}

- [ ] **Timepoints specified**
  - 0h: Baseline
  - {TIMEPOINT_1}h: Early biomarker 1
  - {TIMEPOINT_2}h: Early biomarker 2
  - {TIMEPOINT_FINAL}d: Primary outcome

---

## Phase 5: Computational Prediction (S4 → Sandbox)

- [ ] **S4 convergence achieved**
  - Session ID: {SESSION_ID}
  - S4 convergence ratio: {S4_RATIO}
  - Cross-mirror agreement: {S4_AGREEMENT}

- [ ] **S4 priors extracted**
  - Rhythm priors: ✅ / ❌
  - Center priors: ✅ / ❌
  - Aperture priors: ✅ / ❌
  - Files: `sandbox/states/s4_state.*.json`

- [ ] **Simulation plan created**
  - Plan file: `sandbox/runs/plans/{PLAN_ID}.yaml`
  - Monte Carlo runs: {MC_RUNS} per condition per mirror
  - Consensus rule: {CONSENSUS_RULE}

- [ ] **Simulation executed**
  - Run ID: {RUN_ID}
  - Output directory: `sandbox/runs/outputs/{RUN_ID}/`
  - Predictions file: `predictions.json` ✅ / ❌

- [ ] **Consensus achieved**
  - Cross-mirror agreement: {CONSENSUS_AGREEMENT}
  - Outliers flagged: {OUTLIERS}
  - Predicted P(Factor-High): {PRED_P_HIGH} (95% CI: [{CI_LOW}, {CI_HIGH}])

---

## Phase 6: Mirrors & Context Policy

- [ ] **Mirrors selected**
  - **All 7 mirrors** (recommended for high-stakes predictions)
  - **High-capacity only** (Claude, GPT-4o, Grok, Gemini, DeepSeek)
  - **Local only** (Qwen 1.7B, Llama 3B — for testing)

- [ ] **Context policy selected**
  - **High context** (parallel execution, 25+ cycles)
  - **Medium context** (sequential, 10-15 cycles)
  - **Low context** (minimal, 5 cycles — for rapid prototyping)

- [ ] **Pressure monitoring enabled**
  - Max pressure: 2/5 (halt if any mirror exceeds)
  - Pressure log: `iris_vault/scrolls/{SESSION_ID}/pressure.log`

---

## Phase 7: Budget & Timeline

- [ ] **Budget realistic**
  - Organisms: ${COST_ORGANISMS}
  - Drugs: ${COST_DRUGS}
  - Reagents: ${COST_REAGENTS}
  - Consumables: ${COST_CONSUMABLES}
  - **Total: ${TOTAL_COST}**
  - Available funding: ${AVAILABLE_FUNDING}

- [ ] **Timeline realistic**
  - Preparation: {PREP_DAYS} days
  - Experiment: {EXP_DAYS} days
  - Analysis: {ANALYSIS_DAYS} days
  - **Total: {TOTAL_DAYS} days**
  - Deadline: {DEADLINE}

---

## Phase 8: Risk Assessment

- [ ] **Known confounds identified**
  - Confound 1: {CONFOUND_1} → Mitigation: {MITIGATION_1}
  - Confound 2: {CONFOUND_2} → Mitigation: {MITIGATION_2}

- [ ] **Model limitations acknowledged**
  - S4 priors are phenomenological (not mechanistic)
  - Interaction coefficients are speculative
  - Species-specific prediction (generalization requires validation)

- [ ] **Stopping rules defined**
  - Early success: {EARLY_SUCCESS_RULE}
  - Futility: {FUTILITY_RULE}
  - Harm: {HARM_RULE}

---

## Phase 9: Documentation & Transparency

- [ ] **Pre-registration prepared**
  - Platform: {REGISTRATION_PLATFORM} (OSF / AsPredicted)
  - Draft complete: ✅ / ❌
  - Submitted: ✅ / ❌
  - Registration ID: {REGISTRATION_ID}

- [ ] **Data sharing plan**
  - Raw data repository: {DATA_REPO} (Zenodo / OSF)
  - Analysis code repository: {CODE_REPO} (GitHub)
  - S4 priors included in supplementary materials

- [ ] **Provenance documented**
  - Session ID: {SESSION_ID}
  - Run ID: {RUN_ID}
  - All scrolls archived: ✅ / ❌
  - Memory file updated: ✅ / ❌

---

## Phase 10: Final Approval

- [ ] **PI sign-off**
  - Reviewed by: {PI_NAME}
  - Date: {APPROVAL_DATE}
  - Approved: ✅ / ❌

- [ ] **Collaborator sign-off (if applicable)**
  - Reviewed by: {COLLABORATOR_NAME}
  - Date: {COLLABORATOR_APPROVAL_DATE}
  - Approved: ✅ / ❌

- [ ] **Ready to execute**
  - All checklist items complete
  - Pre-registration submitted
  - Materials ordered
  - Calendar blocked

---

## Status Summary

**Overall Readiness:** {X}/10 phases complete

**Next Action:**
{NEXT_ACTION}

**Blockers:**
{BLOCKERS}

---

**†⟡∞ IRIS Experiment Readiness Checklist v1.0**
